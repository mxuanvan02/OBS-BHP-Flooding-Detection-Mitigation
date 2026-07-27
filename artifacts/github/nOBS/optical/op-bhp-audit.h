#ifndef ns_op_bhp_audit_h
#define ns_op_bhp_audit_h

#include <stdio.h>

#include "op-bhp-guard.h"

/* Versioned, append-only audit stream.  The logger has no callback into the
 * detector and evaluation mappings are intentionally separate from records. */
class BhpAuditLogger {
public:
    BhpAuditLogger();
    explicit BhpAuditLogger(const char* path);
    ~BhpAuditLogger();

    bool open(const char* path);
    void close();
    bool is_open() const;
    const char* path() const;

    void log_bhp_create(double event_time, unsigned long packet_uid,
                        unsigned long burst_id, int ingress,
                        unsigned long claimed_bytes,
                        double reservation_cost);
    void log_observe(const BhpObservation& observation,
                     BhpGuardState state_before);
    void log_detection(const BhpObservation& observation,
                       const BhpDecision& decision);
    void log_decision(const BhpObservation& observation,
                      const BhpDecision& decision);
    void log_action(const BhpObservation& observation,
                    const BhpDecision& decision, bool reservation_attempted,
                    bool cleanup_succeeded);
    void log_outcome(double event_time, unsigned long packet_uid,
                     int ingress, const char* reservation_result,
                     const char* control_result, const char* data_result,
                     bool right_censored);
    void log_legitimate_impact(double event_time, unsigned long control_uid,
                               unsigned long data_uid, int ingress,
                               unsigned long packet_count,
                               unsigned long bytes, const char* reason);

    /* Evaluation-only joins; these are never accepted by BhpGuard. */
    void register_legitimate_pair(unsigned long control_uid,
                                  unsigned long data_uid,
                                  unsigned long packet_count,
                                  unsigned long bytes);
    void register_attack_generation(unsigned long control_uid,
                                    double emit_time);

private:
    BhpAuditLogger(const BhpAuditLogger&);
    BhpAuditLogger& operator=(const BhpAuditLogger&);

    void write_header();
    void record_prefix(const char* type, double event_time);
    static const char* safe(const char* value);

    FILE* stream_;
    char* path_;
    bool header_written_;
};

#endif
