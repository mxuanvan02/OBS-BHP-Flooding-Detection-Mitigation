#ifndef ns_op_bhp_guard_h
#define ns_op_bhp_guard_h

#include <map>

/*
 * This is deliberately a simulator-independent interface.  In particular,
 * it contains no attack label, control_only flag, scenario time, or outcome.
 */
struct BhpObservation {
    BhpObservation();

    double event_time;
    int trusted_ingress;
    unsigned long packet_uid;
    int destination;
    int route_class;
    unsigned long claimed_burst_bytes;
    unsigned long claimed_packet_count;
    double claimed_reservation_cost;
    bool syntax_valid;
    bool range_valid;
    bool route_consistent;
};

enum BhpGuardState {
    BHP_STATE_NORMAL = 0,
    BHP_STATE_LIMITED = 1,
    BHP_STATE_QUARANTINED = 2
};

enum BhpGuardAction {
    BHP_ALLOW = 0,
    BHP_DROP_OVER_PROFILE = 1,
    BHP_QUARANTINE_INGRESS = 2,
    BHP_RELEASE = 3
};

enum BhpGuardReason {
    BHP_REASON_NONE = 0,
    BHP_REASON_EVENT_BUDGET = 1,
    BHP_REASON_RESERVATION_BUDGET = 2,
    BHP_REASON_BOTH_BUDGETS = 3,
    BHP_REASON_MALFORMED = 4,
    BHP_REASON_QUARANTINE_HOLD = 5,
    BHP_REASON_QUARANTINE_RELEASE = 6,
    BHP_REASON_TIME_REGRESSION = 7
};

struct BhpGuardProfile {
    BhpGuardProfile();

    /* Tokens and refill rates are in BHP events and reservation-cost units. */
    double event_capacity;
    double event_rate_per_second;
    double reservation_capacity;
    double reservation_rate_per_second;

    unsigned int violations_to_quarantine;
    double quarantine_hold_down;
    double limited_release_after;
};

struct BhpDecision {
    BhpDecision();

    BhpGuardAction action;
    BhpGuardReason reason;
    BhpGuardState state_before;
    BhpGuardState state_after;

    double observation_time;
    double detection_time;
    double decision_time;
    double state_since;
    double quarantine_until;

    double event_tokens_before;
    double event_tokens_after;
    double reservation_tokens_before;
    double reservation_tokens_after;
    unsigned long observed_events;
    double observed_reservation_cost;

    bool allows_reservation() const;
    bool state_changed() const;
};

class BhpGuard {
public:
    BhpGuard();

    bool configure(const BhpGuardProfile& profile);
    void set_enabled(bool enabled);
    bool enabled() const;
    bool profile_valid() const;
    const BhpGuardProfile& profile() const;

    BhpDecision observe(const BhpObservation& observation);
    void reset();

    static bool validate_profile(const BhpGuardProfile& profile);
    static const char* state_name(BhpGuardState state);
    static const char* action_name(BhpGuardAction action);
    static const char* reason_name(BhpGuardReason reason);

private:
    struct IngressState {
        IngressState();

        BhpGuardState state;
        double state_since;
        double last_event_time;
        double last_violation_time;
        double quarantine_until;
        double event_tokens;
        double reservation_tokens;
        unsigned int consecutive_violations;
        unsigned long observed_events;
        double observed_reservation_cost;
        bool initialized;
    };

    typedef std::map<int, IngressState> StateMap;

    void initialize_state(IngressState& state, double now) const;
    void refill(IngressState& state, double now) const;
    BhpDecision make_base_decision(const BhpObservation& observation,
                                   const IngressState& state) const;
    static bool finite_nonnegative(double value);

    BhpGuardProfile profile_;
    bool enabled_;
    bool profile_valid_;
    StateMap states_;
};

#endif
