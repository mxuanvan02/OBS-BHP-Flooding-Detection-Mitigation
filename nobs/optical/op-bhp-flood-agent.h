#ifndef ns_op_bhp_flood_agent_h
#define ns_op_bhp_flood_agent_h

#include "agent.h"
#include "timer-handler.h"

#include "op-bhp-audit.h"
#include "op-burst_agent.h"

class BHPFloodAgent;

class BHPFloodTimer : public TimerHandler {
public:
    BHPFloodTimer(BHPFloodAgent* agent) : TimerHandler(), agent_(agent) {}

protected:
    virtual void expire(Event* event);

private:
    BHPFloodAgent* agent_;
};

/*
 * Direct PT_OP_BURST producer.  It deliberately has no UDP/CBR input or
 * payload path.  Each control owns its zero-packet phantom descriptor until
 * the control leaves this agent; downstream ownership transfer is represented
 * by the existing hdr_burst::burst pointer invariant.
 */
class BHPFloodAgent : public Agent {
public:
    BHPFloodAgent();
    virtual ~BHPFloodAgent();

    virtual int command(int argc, const char*const* argv);
    virtual void recv(Packet* packet, Handler* handler);

    void start();
    void stop();
    void emit();
    void timer_expired();
    bool running() const;

private:
    void free_owned(Packet* control);
    Packet* make_control(Packet** phantom);

    BHPFloodTimer timer_;
    BhpAuditLogger audit_;
    unsigned long next_burst_id_;
    int destination_;
    int claimedBurstBytes_;
    int claimedPacketCount_;
    double interval_;
    int trustedAttachment_;
    int routeClass_;
    int running_;
};

#endif
