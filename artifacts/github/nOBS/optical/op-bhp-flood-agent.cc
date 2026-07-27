#include "op-bhp-flood-agent.h"

#include <string.h>

#include "ip.h"
#include "scheduler.h"
#include "src_rtg/hdr_src.h"

static class BHPFloodAgentClass : public TclClass {
public:
    BHPFloodAgentClass() : TclClass("Agent/BHPFlood") {}
    TclObject* create(int, const char*const*) { return new BHPFloodAgent(); }
} class_bhp_flood_agent;

BHPFloodAgent::BHPFloodAgent()
    : Agent(PT_OP_BURST), timer_(this), next_burst_id_(1), destination_(0),
      claimedBurstBytes_(0), claimedPacketCount_(1), interval_(0.0),
      trustedAttachment_(-1), routeClass_(-1), running_(0)
{
    bind("destination_", &destination_);
    bind("claimedBurstBytes_", &claimedBurstBytes_);
    bind("claimedPacketCount_", &claimedPacketCount_);
    bind_time("interval_", &interval_);
    bind("trustedAttachment_", &trustedAttachment_);
    bind("routeClass_", &routeClass_);
}

BHPFloodAgent::~BHPFloodAgent()
{
    stop();
}

bool BHPFloodAgent::running() const
{
    return running_ != 0;
}

void BHPFloodAgent::start()
{
    if (running_)
        return;
    running_ = 1;
    emit();
    if (running_ && interval_ > 0.0)
        timer_.sched(interval_);
}

void BHPFloodAgent::stop()
{
    running_ = 0;
    timer_.force_cancel();
}

void BHPFloodTimer::expire(Event*)
{
    agent_->timer_expired();
}

void BHPFloodAgent::timer_expired()
{
    emit();
    if (running_ && interval_ > 0.0)
        timer_.sched(interval_);
}

Packet* BHPFloodAgent::make_control(Packet** phantom)
{
    Packet* control = allocpkt();
    Packet* data = allocpkt();
    hdr_cmn* cmn_control = hdr_cmn::access(control);
    hdr_cmn* cmn_data = hdr_cmn::access(data);
    hdr_burst* burst_control = hdr_burst::access(control);
    hdr_burst* burst_data = hdr_burst::access(data);
    hdr_ip* ip_control = hdr_ip::access(control);
    hdr_ip* ip_data = hdr_ip::access(data);
    hdr_src* src_control = hdr_src::access(control);
    hdr_src* src_data = hdr_src::access(data);

    cmn_control->ptype() = PT_OP_BURST;
    cmn_data->ptype() = PT_OP_BURST;
    cmn_control->size() = BURST_HEADER;
    cmn_data->size() = claimedBurstBytes_;
    cmn_control->src_rt_valid = 0;
    cmn_data->src_rt_valid = 0;

    memset(src_control, 0, sizeof(hdr_src));
    memset(src_data, 0, sizeof(hdr_src));
    ip_control->saddr() = addr();
    ip_control->daddr() = destination_;
    ip_control->ttl() = IP_DEF_TTL;
    ip_data->saddr() = addr();
    ip_data->daddr() = destination_;
    ip_data->ttl() = IP_DEF_TTL;

    burst_control->send_time = Scheduler::instance().clock();
    burst_control->created_time = burst_control->send_time;
    burst_control->burst_size = (unsigned int)claimedBurstBytes_;
    burst_control->packet_num = (unsigned int)claimedPacketCount_;
    burst_control->burst_type = 0;
    burst_control->seg_type = 0;
    burst_control->burst_id = next_burst_id_++;
    burst_control->route_length = 0;
    burst_control->route_length_tot = 0;
    burst_control->delayedresv = 0.0;
    burst_control->linkspeed = (unsigned int)LINKSPEED;
    burst_control->lambda = -1;
    burst_control->source = ip_control->saddr();
    burst_control->destination = destination_;
    burst_control->flow = 0;
    burst_control->ack = 0;
    burst_control->first_link = 1;
    burst_control->drop = 0;
    burst_control->burst = data;

    burst_data->send_time = burst_control->send_time;
    burst_data->created_time = burst_control->created_time;
    burst_data->burst_size = (unsigned int)claimedBurstBytes_;
    burst_data->packet_num = 0; /* phantom: never contains or sends payload */
    burst_data->burst_type = 1;
    burst_data->seg_type = 0;
    burst_data->burst_id = burst_control->burst_id;
    burst_data->route_length = 0;
    burst_data->route_length_tot = 0;
    burst_data->delayedresv = 0.0;
    burst_data->linkspeed = burst_control->linkspeed;
    burst_data->lambda = -1;
    burst_data->source = burst_control->source;
    burst_data->destination = destination_;
    burst_data->flow = 0;
    burst_data->ack = 0;
    burst_data->first_link = 1;
    burst_data->drop = 0;
    burst_data->burst = 0;
    *phantom = data;
    return control;
}

void BHPFloodAgent::emit()
{
    if (target_ == 0 || destination_ < 0 || claimedBurstBytes_ <= 0 ||
        claimedPacketCount_ <= 0)
        return;

    Packet* phantom = 0;
    Packet* control = make_control(&phantom);
    hdr_burst* header = hdr_burst::access(control);
    hdr_cmn* common = hdr_cmn::access(control);
    double now = Scheduler::instance().clock();
    double cost = (double)header->burst_size * 8.0 /
                  (double)header->linkspeed;

    audit_.log_bhp_create(now, (unsigned long)common->uid(),
                          header->burst_id, trustedAttachment_,
                          header->burst_size, cost);
    send(control, 0);
    /* Ownership is transferred through hdr_burst::burst with the control. */
    (void)phantom;
}

void BHPFloodAgent::free_owned(Packet* control)
{
    if (control == 0)
        return;
    hdr_burst* header = hdr_burst::access(control);
    Packet* phantom = header->burst;
    header->burst = 0;
    if (phantom != 0)
        Packet::free(phantom);
    Packet::free(control);
}

void BHPFloodAgent::recv(Packet* packet, Handler*)
{
    /* A generator is not a sink; reclaim unexpected feedback safely. */
    free_owned(packet);
}

int BHPFloodAgent::command(int argc, const char*const* argv)
{
    if (argc == 2) {
        if (strcmp(argv[1], "start") == 0) {
            start();
            return TCL_OK;
        }
        if (strcmp(argv[1], "stop") == 0) {
            stop();
            return TCL_OK;
        }
        if (strcmp(argv[1], "emit") == 0) {
            emit();
            return TCL_OK;
        }
    } else if (argc == 3 && strcmp(argv[1], "audit-log") == 0) {
        return audit_.open(argv[2]) ? TCL_OK : TCL_ERROR;
    }
    return Agent::command(argc, argv);
}
