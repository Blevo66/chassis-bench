# RS PRO M12 8-pin A-coded FRONT panel-mount sockets, pre-wired 500 mm, shielded, M16x1.5 clamp nut
#   female 250-0736 (brain box: it carries the 5 V out, so its contacts are the shrouded ones)
#   male   250-0742 (screen pod)
# Joel picked these 2026-11-25. Only the THREAD (M16x1.5) and the front-mount style are from RS. Every length,
# across-flats and the plug envelope below are TYPICAL / GUESSED values for this style of part: measure the real
# parts with calipers and update the numbers here.
# Local frame: u along the socket axis, u=0 at the wall's OUTER face, +u = outward. Front-mount = body flange
# outside (O-ring under it), M16 nut inside.
import cadquery as cq, math
FL_AF,FL_T   = 20.0,4.0     # outside body hex/flange (guess)
CPL_R,CPL_L  = 6.5,10.0     # M12x1 coupling end (guess)
THR_R,THR_L  = 7.9,12.0     # M16x1.5 body behind the outer face, incl. the wall (guess)
NUT_AF,NUT_T = 19.0,3.0     # M16 thin nut inside (guess)
LEAD_R,LEAD_L= 3.0,8.0      # 8 leads leave the potted end; bend room before they turn (guess)
HOLE_R       = 8.1          # 16.2 hole for the M16x1.5 thread
def socket(seg,hseg,W,leads=True):
    """seg(u0,L,r) / hseg(u0,L,af) build cylinders/hexes along u in the caller's frame. W = wall thickness
    the nut clamps (incl. any clearance on the inner face)."""
    s=(hseg(0,FL_T,FL_AF).union(seg(FL_T,CPL_L,CPL_R))
       .union(seg(-THR_L,THR_L,THR_R))
       .union(hseg(-W-NUT_T,NUT_T,NUT_AF)))
    return s.union(seg(-THR_L-LEAD_L,LEAD_L,LEAD_R)) if leads else s
def plug(seg):
    u=FL_T+0.2      # mating cable plug: coupling nut (screws over the M12 end) + grip + 6.0 mm cable (RS 283-4972; head sizes guessed)
    p=seg(u,14,10.0).union(seg(u+14,31,7.5)).union(seg(u+45,30,3.0))
    return p.cut(seg(FL_T,CPL_L+0.5,CPL_R+0.2))   # hollow where it goes over the socket's coupling
