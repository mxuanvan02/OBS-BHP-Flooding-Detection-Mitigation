#include "op-bhp-guard.h"

#include <float.h>

BhpObservation::BhpObservation()
    : event_time(0.0), trusted_ingress(-1), packet_uid(0), destination(-1),
      route_class(-1), claimed_burst_bytes(0), claimed_packet_count(0),
      claimed_reservation_cost(0.0), syntax_valid(false), range_valid(false),
      route_consistent(false)
{
}

BhpGuardProfile::BhpGuardProfile()
    : event_capacity(0.0), event_rate_per_second(0.0),
      reservation_capacity(0.0), reservation_rate_per_second(0.0),
      violations_to_quarantine(0), quarantine_hold_down(0.0),
      limited_release_after(0.0)
{
}

BhpDecision::BhpDecision()
    : action(BHP_ALLOW), reason(BHP_REASON_NONE),
      state_before(BHP_STATE_NORMAL), state_after(BHP_STATE_NORMAL),
      observation_time(0.0), detection_time(-1.0), decision_time(0.0),
      state_since(0.0), quarantine_until(0.0), event_tokens_before(0.0),
      event_tokens_after(0.0), reservation_tokens_before(0.0),
      reservation_tokens_after(0.0), observed_events(0),
      observed_reservation_cost(0.0)
{
}

bool BhpDecision::allows_reservation() const
{
    return action == BHP_ALLOW || action == BHP_RELEASE;
}

bool BhpDecision::state_changed() const
{
    return state_before != state_after;
}

BhpGuard::IngressState::IngressState()
    : state(BHP_STATE_NORMAL), state_since(0.0), last_event_time(0.0),
      last_violation_time(-1.0), quarantine_until(0.0), event_tokens(0.0),
      reservation_tokens(0.0), consecutive_violations(0),
      observed_events(0), observed_reservation_cost(0.0), initialized(false)
{
}

BhpGuard::BhpGuard() : enabled_(false), profile_valid_(false)
{
}

bool BhpGuard::finite_nonnegative(double value)
{
    return value == value && value >= 0.0 && value <= DBL_MAX;
}

bool BhpGuard::validate_profile(const BhpGuardProfile& profile)
{
    return finite_nonnegative(profile.event_capacity) &&
           finite_nonnegative(profile.event_rate_per_second) &&
           finite_nonnegative(profile.reservation_capacity) &&
           finite_nonnegative(profile.reservation_rate_per_second) &&
           profile.event_capacity > 0.0 &&
           profile.reservation_capacity > 0.0 &&
           profile.violations_to_quarantine >= 2 &&
           finite_nonnegative(profile.quarantine_hold_down) &&
           profile.quarantine_hold_down > 0.0 &&
           finite_nonnegative(profile.limited_release_after) &&
           profile.limited_release_after > 0.0;
}

bool BhpGuard::configure(const BhpGuardProfile& profile)
{
    if (!validate_profile(profile))
        return false;
    profile_ = profile;
    profile_valid_ = true;
    reset();
    return true;
}

void BhpGuard::set_enabled(bool enabled)
{
    enabled_ = enabled;
}

bool BhpGuard::enabled() const
{
    return enabled_;
}

bool BhpGuard::profile_valid() const
{
    return profile_valid_;
}

const BhpGuardProfile& BhpGuard::profile() const
{
    return profile_;
}

void BhpGuard::reset()
{
    states_.clear();
}

void BhpGuard::initialize_state(IngressState& state, double now) const
{
    state.state = BHP_STATE_NORMAL;
    state.state_since = now;
    state.last_event_time = now;
    state.last_violation_time = -1.0;
    state.quarantine_until = 0.0;
    state.event_tokens = profile_.event_capacity;
    state.reservation_tokens = profile_.reservation_capacity;
    state.consecutive_violations = 0;
    state.observed_events = 0;
    state.observed_reservation_cost = 0.0;
    state.initialized = true;
}

void BhpGuard::refill(IngressState& state, double now) const
{
    double elapsed = now - state.last_event_time;
    if (elapsed <= 0.0)
        return;

    state.event_tokens += elapsed * profile_.event_rate_per_second;
    if (state.event_tokens > profile_.event_capacity)
        state.event_tokens = profile_.event_capacity;

    state.reservation_tokens += elapsed * profile_.reservation_rate_per_second;
    if (state.reservation_tokens > profile_.reservation_capacity)
        state.reservation_tokens = profile_.reservation_capacity;
}

BhpDecision BhpGuard::make_base_decision(
    const BhpObservation& observation, const IngressState& state) const
{
    BhpDecision decision;
    decision.state_before = state.state;
    decision.state_after = state.state;
    decision.observation_time = observation.event_time;
    decision.decision_time = observation.event_time;
    decision.state_since = state.state_since;
    decision.quarantine_until = state.quarantine_until;
    decision.event_tokens_before = state.event_tokens;
    decision.event_tokens_after = state.event_tokens;
    decision.reservation_tokens_before = state.reservation_tokens;
    decision.reservation_tokens_after = state.reservation_tokens;
    decision.observed_events = state.observed_events;
    decision.observed_reservation_cost = state.observed_reservation_cost;
    return decision;
}

BhpDecision BhpGuard::observe(const BhpObservation& observation)
{
    IngressState& state = states_[observation.trusted_ingress];
    if (!state.initialized)
        initialize_state(state, observation.event_time);

    BhpDecision decision = make_base_decision(observation, state);

    if (!enabled_) {
        state.observed_events++;
        state.observed_reservation_cost += observation.claimed_reservation_cost;
        state.last_event_time = observation.event_time;
        decision.observed_events = state.observed_events;
        decision.observed_reservation_cost = state.observed_reservation_cost;
        return decision;
    }

    /* A configured-but-invalid guard never admits traffic. */
    if (!profile_valid_) {
        decision.action = BHP_QUARANTINE_INGRESS;
        decision.reason = BHP_REASON_MALFORMED;
        return decision;
    }

    if (!finite_nonnegative(observation.event_time) ||
        observation.trusted_ingress < 0 ||
        observation.destination < 0 ||
        observation.claimed_burst_bytes == 0 ||
        observation.claimed_packet_count == 0 ||
        !finite_nonnegative(observation.claimed_reservation_cost) ||
        !observation.syntax_valid || !observation.range_valid ||
        !observation.route_consistent) {
        decision.action = BHP_DROP_OVER_PROFILE;
        decision.reason = BHP_REASON_MALFORMED;
        return decision;
    }

    if (observation.event_time < state.last_event_time) {
        decision.action = BHP_DROP_OVER_PROFILE;
        decision.reason = BHP_REASON_TIME_REGRESSION;
        return decision;
    }

    refill(state, observation.event_time);
    state.last_event_time = observation.event_time;
    state.observed_events++;
    state.observed_reservation_cost += observation.claimed_reservation_cost;

    decision = make_base_decision(observation, state);

    if (state.state == BHP_STATE_QUARANTINED &&
        observation.event_time < state.quarantine_until) {
        decision.action = BHP_QUARANTINE_INGRESS;
        decision.reason = BHP_REASON_QUARANTINE_HOLD;
        return decision;
    }

    bool released = false;
    if (state.state == BHP_STATE_QUARANTINED) {
        state.state = BHP_STATE_LIMITED;
        state.state_since = observation.event_time;
        state.consecutive_violations = 0;
        released = true;
    } else if (state.state == BHP_STATE_LIMITED &&
               state.last_violation_time >= 0.0 &&
               observation.event_time - state.last_violation_time >=
                   profile_.limited_release_after) {
        state.state = BHP_STATE_NORMAL;
        state.state_since = observation.event_time;
        state.consecutive_violations = 0;
    }

    const bool event_ok = state.event_tokens >= 1.0;
    const bool reservation_ok =
        state.reservation_tokens >= observation.claimed_reservation_cost;

    decision.event_tokens_before = state.event_tokens;
    decision.reservation_tokens_before = state.reservation_tokens;

    if (event_ok && reservation_ok) {
        state.event_tokens -= 1.0;
        state.reservation_tokens -= observation.claimed_reservation_cost;
        state.consecutive_violations = 0;
        decision.action = released ? BHP_RELEASE : BHP_ALLOW;
        decision.reason = released ? BHP_REASON_QUARANTINE_RELEASE
                                   : BHP_REASON_NONE;
    } else {
        state.consecutive_violations++;
        state.last_violation_time = observation.event_time;
        decision.reason = !event_ok && !reservation_ok
                              ? BHP_REASON_BOTH_BUDGETS
                              : (!event_ok ? BHP_REASON_EVENT_BUDGET
                                           : BHP_REASON_RESERVATION_BUDGET);

        if (state.state == BHP_STATE_NORMAL) {
            state.state = BHP_STATE_LIMITED;
            state.state_since = observation.event_time;
            decision.detection_time = observation.event_time;
        }

        if (state.consecutive_violations >=
            profile_.violations_to_quarantine) {
            state.state = BHP_STATE_QUARANTINED;
            state.state_since = observation.event_time;
            state.quarantine_until =
                observation.event_time + profile_.quarantine_hold_down;
            decision.action = BHP_QUARANTINE_INGRESS;
            decision.detection_time = observation.event_time;
        } else {
            decision.action = BHP_DROP_OVER_PROFILE;
        }
    }

    decision.state_after = state.state;
    decision.state_since = state.state_since;
    decision.quarantine_until = state.quarantine_until;
    decision.event_tokens_after = state.event_tokens;
    decision.reservation_tokens_after = state.reservation_tokens;
    decision.observed_events = state.observed_events;
    decision.observed_reservation_cost = state.observed_reservation_cost;
    return decision;
}

const char* BhpGuard::state_name(BhpGuardState state)
{
    switch (state) {
    case BHP_STATE_NORMAL: return "NORMAL";
    case BHP_STATE_LIMITED: return "LIMITED";
    case BHP_STATE_QUARANTINED: return "QUARANTINED";
    }
    return "UNKNOWN";
}

const char* BhpGuard::action_name(BhpGuardAction action)
{
    switch (action) {
    case BHP_ALLOW: return "ALLOW";
    case BHP_DROP_OVER_PROFILE: return "DROP_OVER_PROFILE";
    case BHP_QUARANTINE_INGRESS: return "QUARANTINE_INGRESS";
    case BHP_RELEASE: return "RELEASE";
    }
    return "UNKNOWN";
}

const char* BhpGuard::reason_name(BhpGuardReason reason)
{
    switch (reason) {
    case BHP_REASON_NONE: return "NONE";
    case BHP_REASON_EVENT_BUDGET: return "EVENT_BUDGET";
    case BHP_REASON_RESERVATION_BUDGET: return "RESERVATION_BUDGET";
    case BHP_REASON_BOTH_BUDGETS: return "BOTH_BUDGETS";
    case BHP_REASON_MALFORMED: return "MALFORMED";
    case BHP_REASON_QUARANTINE_HOLD: return "QUARANTINE_HOLD";
    case BHP_REASON_QUARANTINE_RELEASE: return "QUARANTINE_RELEASE";
    case BHP_REASON_TIME_REGRESSION: return "TIME_REGRESSION";
    }
    return "UNKNOWN";
}
