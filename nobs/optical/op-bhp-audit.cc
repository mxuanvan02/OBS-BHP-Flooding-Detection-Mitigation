#include "op-bhp-audit.h"

#include <string.h>

static const int BHP_AUDIT_SCHEMA_VERSION = 1;

BhpAuditLogger::BhpAuditLogger() : stream_(0), path_(0), header_written_(false)
{
}

BhpAuditLogger::BhpAuditLogger(const char* path)
    : stream_(0), path_(0), header_written_(false)
{
    open(path);
}

BhpAuditLogger::~BhpAuditLogger()
{
    close();
}

bool BhpAuditLogger::open(const char* path)
{
    close();
    if (path == 0 || *path == '\0')
        return false;

    stream_ = fopen(path, "a");
    if (stream_ == 0)
        return false;

    /* Multiple OpSRAgents may share one append-only lifecycle log.  Write
     * its schema preamble exactly once, when the file is first created. */
    if (fseek(stream_, 0, SEEK_END) != 0) {
        close();
        return false;
    }
    header_written_ = ftell(stream_) > 0;

    path_ = new char[strlen(path) + 1];
    strcpy(path_, path);
    write_header();
    return true;
}

void BhpAuditLogger::close()
{
    if (stream_ != 0) {
        fflush(stream_);
        fclose(stream_);
        stream_ = 0;
    }
    delete [] path_;
    path_ = 0;
    header_written_ = false;
}

bool BhpAuditLogger::is_open() const
{
    return stream_ != 0;
}

const char* BhpAuditLogger::path() const
{
    return path_ == 0 ? "" : path_;
}

const char* BhpAuditLogger::safe(const char* value)
{
    return value == 0 ? "" : value;
}

void BhpAuditLogger::write_header()
{
    if (stream_ == 0 || header_written_)
        return;
    fprintf(stream_, "# BHP_AUDIT schema=%d format=tab-separated append-only\n",
            BHP_AUDIT_SCHEMA_VERSION);
    fprintf(stream_,
            "# type,event_time,packet_uid,burst_id,ingress,destination,route_class,claimed_bytes,claimed_packets,reservation_cost,state_before,state_after,action,reason,detection_time,decision_time,action_time,reservation_attempted,cleanup_succeeded,reservation_result,control_result,data_result,right_censored,data_uid,impact_packets,impact_bytes,impact_reason\n");
    fflush(stream_);
    header_written_ = true;
}

void BhpAuditLogger::record_prefix(const char* type, double event_time)
{
    if (stream_ == 0)
        return;
    fprintf(stream_, "%s,%.17g,", safe(type), event_time);
}

void BhpAuditLogger::log_bhp_create(double event_time, unsigned long packet_uid,
                                    unsigned long burst_id, int ingress,
                                    unsigned long claimed_bytes,
                                    double reservation_cost)
{
    record_prefix("BHP_CREATE", event_time);
    fprintf(stream_, "%lu,%lu,%d,-1,-1,%lu,0,%.17g,,,,,,,,,,,,,,,,,\n",
            packet_uid, burst_id, ingress, claimed_bytes, reservation_cost);
    fflush(stream_);
}

void BhpAuditLogger::log_observe(const BhpObservation& observation,
                                 BhpGuardState state_before)
{
    record_prefix("OBSERVE", observation.event_time);
    fprintf(stream_, "%lu,0,%d,%d,%d,%lu,%lu,%.17g,%s,,,,,,,,,,,,,,,,,,\n",
            observation.packet_uid, observation.trusted_ingress,
            observation.destination, observation.route_class,
            observation.claimed_burst_bytes, observation.claimed_packet_count,
            observation.claimed_reservation_cost,
            BhpGuard::state_name(state_before));
    fflush(stream_);
}

void BhpAuditLogger::log_detection(const BhpObservation& observation,
                                   const BhpDecision& decision)
{
    if (!decision.state_changed() && decision.detection_time < 0.0)
        return;
    record_prefix("DETECT", decision.detection_time < 0.0
                              ? observation.event_time : decision.detection_time);
    fprintf(stream_, "%lu,0,%d,%d,%d,%lu,%lu,%.17g,%s,%s,%s,%s,%.17g,%.17g,,,,,,,,,,,,\n",
            observation.packet_uid, observation.trusted_ingress,
            observation.destination, observation.route_class,
            observation.claimed_burst_bytes, observation.claimed_packet_count,
            observation.claimed_reservation_cost,
            BhpGuard::state_name(decision.state_before),
            BhpGuard::state_name(decision.state_after),
            BhpGuard::action_name(decision.action),
            BhpGuard::reason_name(decision.reason), decision.detection_time,
            decision.decision_time);
    fflush(stream_);
}

void BhpAuditLogger::log_decision(const BhpObservation& observation,
                                  const BhpDecision& decision)
{
    record_prefix("DECIDE", decision.decision_time);
    fprintf(stream_, "%lu,0,%d,%d,%d,%lu,%lu,%.17g,%s,%s,%s,%s,%.17g,%.17g,,,,,,,,,,,,\n",
            observation.packet_uid, observation.trusted_ingress,
            observation.destination, observation.route_class,
            observation.claimed_burst_bytes, observation.claimed_packet_count,
            observation.claimed_reservation_cost,
            BhpGuard::state_name(decision.state_before),
            BhpGuard::state_name(decision.state_after),
            BhpGuard::action_name(decision.action),
            BhpGuard::reason_name(decision.reason), decision.detection_time,
            decision.decision_time);
    fflush(stream_);
}

void BhpAuditLogger::log_action(const BhpObservation& observation,
                                const BhpDecision& decision,
                                bool reservation_attempted,
                                bool cleanup_succeeded)
{
    record_prefix("ACT", decision.decision_time);
    fprintf(stream_, "%lu,0,%d,%d,%d,%lu,%lu,%.17g,%s,%s,%s,%s,%.17g,%.17g,%.17g,%d,%d,,,,,,,,\n",
            observation.packet_uid, observation.trusted_ingress,
            observation.destination, observation.route_class,
            observation.claimed_burst_bytes, observation.claimed_packet_count,
            observation.claimed_reservation_cost,
            BhpGuard::state_name(decision.state_before),
            BhpGuard::state_name(decision.state_after),
            BhpGuard::action_name(decision.action),
            BhpGuard::reason_name(decision.reason), decision.detection_time,
            decision.decision_time, decision.decision_time,
            reservation_attempted ? 1 : 0, cleanup_succeeded ? 1 : 0);
    fflush(stream_);
}

void BhpAuditLogger::log_outcome(double event_time, unsigned long packet_uid,
                                 int ingress, const char* reservation_result,
                                 const char* control_result,
                                 const char* data_result, bool right_censored)
{
    if (stream_ == 0)
        return;
    record_prefix("OUTCOME", event_time);
    fprintf(stream_, "%lu,0,%d,-1,-1,0,0,0,,,,,,,,,,%s,%s,%s,%d,,,,\n",
            packet_uid, ingress, safe(reservation_result),
            safe(control_result), safe(data_result), right_censored ? 1 : 0);
    fflush(stream_);
}

void BhpAuditLogger::log_legitimate_impact(double event_time,
                                           unsigned long control_uid,
                                           unsigned long data_uid, int ingress,
                                           unsigned long packet_count,
                                           unsigned long bytes,
                                           const char* reason)
{
    record_prefix("LEGIT_IMPACT", event_time);
    fprintf(stream_, "%lu,0,%d,-1,-1,0,0,0,0,,,,,,,,,,,%lu,%lu,%lu,%s\n",
            control_uid, ingress, data_uid, packet_count, bytes,
            safe(reason));
    fflush(stream_);
}

void BhpAuditLogger::register_legitimate_pair(unsigned long, unsigned long,
                                              unsigned long, unsigned long)
{
    /* Evaluation registry is intentionally not written to the detector log. */
}

void BhpAuditLogger::register_attack_generation(unsigned long, double)
{
    /* Generation metadata is joined by an evaluator after admission. */
}
