import json, subprocess, os, math, bisect
T = json.load(open("production/transcript_0717.json"))
words = [(w["s"], w["e"], w["w"].strip()) for seg in T for w in seg["words"]]
FF="ffmpeg"; W,H,FPS=1920,1080,30
os.makedirs("seg", exist_ok=True)
GRADE="eq=contrast=1.03:saturation=1.02:brightness=0.035:gamma=1.05,colorbalance=rm=.01:bm=-.01"
ENERGY=float(os.environ.get("ENERGY","0"))   # 0 = calm (META), 1 = punchy (HERO)
GAPTHR=0.26-0.04*ENERGY; PAD=0.07-0.02*ENERGY; TAIL=0.05-0.02*ENERGY
SUBLEN=3.2-0.6*ENERGY; CARDD=1.6-0.2*ENERGY; INTRO=1.4; ENDD=2.6
# FULL SCRIPT — every section, best take, b-roll locked to the exact spoken word
ACTS=[
  dict(name="hook", s=39.60, e=70.55,
       heads=[(44.16,"LONGEVITY ADVICE IS EVERYWHERE."),(58.90,"YOUR DIRECT PATH TO A LONGER, BETTER LIFE.")],
       broll=[("noise_screens",44.16,4.10),("site_yoga",53.90,3.10)]),
  dict(name="why", s=73.90, e=101.55,
       heads=[], broll=[]),
  dict(name="pillars", s=127.45, e=160.65,
       heads=[(128.40,"MASTER THE SIX PILLARS FOR A LONGER, BETTER LIFE.")],
       broll=[("site_nutrition",137.14,0.90),("site_sleep",138.12,1.00),
              ("swimmer_dawn",139.20,1.45),("site_supplements",140.72,1.70),
              ("site_wearables",144.14,1.90)]),
  dict(name="proof", s=165.45, e=189.75,
       heads=[(171.00,"YOUR BIOMARKERS. YOUR DATA. YOUR LONGEVITY PROTOCOL.")],
       broll=[("data_curve",171.20,4.60)]),
  dict(name="academy", s=195.85, e=221.00,
       heads=[(196.00,"THE LONGEVITY BLUEPRINT — TAUGHT BY LONGEVITY'S LEADING EXPERTS.")],
       broll=[("instructors",197.4,4.20),("online_session",205.16,3.30),("oximeter_data",213.40,4.40)]),
  dict(name="close", s=377.55, e=401.85,
       heads=[], broll=[]),
]
CARDS_AFTER={"academy":"cta3"}
idx=0; PLAN=[]; SEG=[]; out_t=0.0; card_idxs=[]; heads=[]; music_marks={}
def enc_her(ss,de):
    global idx,out_t; idx+=1; PLAN.append(de); SEG.append((ss,ss+de,out_t)); out_t+=de
    vf=GRADE+f",scale={W}:{H},fps={FPS}"
    subprocess.run([FF,"-y","-loglevel","error","-ss",str(ss),"-t",str(de),"-i","base.mp4",
      "-vf",vf,"-af",f"afade=t=in:d=0.02,afade=t=out:st={max(0,de-0.02)}:d=0.02",
      "-c:v","libx264","-crf","17","-preset","fast","-pix_fmt","yuv420p",
      "-c:a","aac","-ar","48000","-ac","2",f"seg/{idx:03d}.mp4"],check=True)
def enc_broll(clip,de,a_ss):
    global idx,out_t
    if not os.path.exists(f"{clip}.mp4"):
        print("MISSING broll, using her footage instead:",clip); enc_her(a_ss,de); return
    idx+=1; PLAN.append(de); SEG.append((a_ss,a_ss+de,out_t)); out_t+=de
    if clip=="noise_screens":
        vf=(f"crop=w=iw*0.80:h=ih*0.80:x=(iw-ow)*0.5*min(1\\,t/{de}):y=(ih-oh)*0.25,"
            f"scale={W}:{H}:flags=lanczos,fps={FPS},"+GRADE)
    else:
        vf=(f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
            +GRADE+(",eq=brightness=0.10:saturation=1.05" if clip=="oximeter_data" else ",eq=brightness=0.04")+",unsharp=5:5:0.4")
    subprocess.run([FF,"-y","-loglevel","error","-stream_loop","-1","-t",str(de),"-i",f"{clip}.mp4",
      "-ss",str(a_ss),"-t",str(de),"-i","base.mp4","-map","0:v","-map","1:a","-vf",vf,
      "-af",f"afade=t=in:d=0.02,afade=t=out:st={max(0,de-0.02)}:d=0.02",
      "-c:v","libx264","-crf","17","-preset","fast","-pix_fmt","yuv420p",
      "-c:a","aac","-ar","48000","-ac","2",f"seg/{idx:03d}.mp4"],check=True)
def enc_card(png,de):
    global idx,out_t; idx+=1; PLAN.append(de); out_t+=de
    subprocess.run([FF,"-y","-loglevel","error","-loop","1","-t",str(de),"-i",png,
      "-f","lavfi","-t",str(de),"-i","anullsrc=r=48000:cl=stereo",
      "-vf",f"scale={W}:{H},fps={FPS},fade=t=in:d=0.35,fade=t=out:st={de-0.35}:d=0.35",
      "-c:v","libx264","-crf","17","-preset","fast","-pix_fmt","yuv420p",
      "-c:a","aac","-shortest",f"seg/{idx:03d}.mp4"],check=True)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
NAVY=(14,31,72); DEEP=(8,22,52); BONE=(245,242,234); ACC=(143,180,245); MUT=(138,147,168)
bg=Image.new("RGB",(W,H)); px=bg.load()
for yy in range(H):
    f=yy/H; row=tuple(int(NAVY[i]+(DEEP[i]-NAVY[i])*f) for i in range(3))
    for xx in range(W): px[xx,yy]=row
vig=Image.new("L",(W,H),0); dv=ImageDraw.Draw(vig)
dv.ellipse([-W*0.25,-H*0.35,W*1.25,H*1.35],fill=70)
vig=vig.filter(ImageFilter.GaussianBlur(220))
bg=Image.composite(bg,Image.new("RGB",(W,H),(4,12,30)),vig)
bg.save("cardbg.png")
F_DISP=lambda s: ImageFont.truetype("fonts/Fraunces-Display.ttf",s)
F_INT=lambda s: ImageFont.truetype("fonts/Inter-Bold.ttf",s)
def strip_png(spans,font,tag,strike_idx=None,pad=30):
    probe=Image.new("RGBA",(10,10)); dp=ImageDraw.Draw(probe)
    ws=[dp.textlength(t,font=font) for t,_ in spans]
    asc,desc=font.getmetrics()
    Wt=int(sum(ws))+pad*2; Ht=asc+desc+pad*2
    im=Image.new("RGBA",(Wt,Ht),(0,0,0,0)); d=ImageDraw.Draw(im)
    x=pad
    for k,(t,col) in enumerate(spans):
        d.text((x,pad),t,font=font,fill=col+(255,))
        if strike_idx is not None and k==strike_idx:
            ym=pad+int(asc*0.72); d.line([x+6,ym,x+ws[k]-6,ym],fill=col+(255,),width=9)
        x+=ws[k]
    im.save(f"{tag}.png"); return Wt,Ht
CARD_SPECS={
  "cta1":[("k","LONGEVITY LIFE ACADEMY",None),
          ("m",[("A longer life,",BONE)],None),
          ("m",[("taught properly.",ACC)],None)],
  "cta2":[("k","18 LIVE SESSIONS · SIX PILLARS",None),
          ("m",[("Master the path,",BONE)],None),
          ("m",[("week by week.",ACC)],None)],
  "cta3":[("k","20% OFF · THIS WEEK ONLY",None),
          ("m",[("$1,500",MUT),("  $1,200",BONE)],0),
          ("m",[("Claim your seat.",ACC)],None)],
}
def enc_anim_card(cname,de):
    global idx,out_t; idx+=1; PLAN.append(de); out_t+=de
    spec=CARD_SPECS[cname]; layers=[]
    for j,item in enumerate(spec):
        kind,payload,sk=item
        if kind=="k":
            wpx,hpx=strip_png([(payload,ACC)],F_INT(34),f"c_{cname}_{j}")
        else:
            wpx,hpx=strip_png(payload,F_DISP(150),f"c_{cname}_{j}",strike_idx=sk)
        layers.append((f"c_{cname}_{j}.png",wpx,hpx))
    total=sum(h for _,_,h in layers)+2*24; y0=(H-total)//2; NF=int(de*FPS)
    ins=["-framerate","30","-loop","1","-t",str(de),"-i","cardbg.png"]
    fl=[f"[0:v]scale=2200:1238,zoompan=z='1+0.04*on/{NF}':d=1:x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':s={W}x{H}:fps={FPS}[bg]"]
    prev="bg"; y=y0
    for j,(fn,wpx,hpx) in enumerate(layers):
        ins+=["-framerate","30","-loop","1","-t",str(de),"-i",fn]
        st=0.10+j*0.14
        fl.append(f"[{j+1}:v]format=rgba,fade=t=in:st={st}:d=0.30:alpha=1,fade=t=out:st={de-0.28}:d=0.26:alpha=1[l{j}]")
        fl.append(f"[{prev}][l{j}]overlay=x=(W-w)/2:y='{y}+42*exp(-9*max(0\\,t-{st}))'[o{j}]")
        prev=f"o{j}"; y+=hpx+24
    fl.append(f"[{prev}]fade=t=in:d=0.18:color=0x0E1F48,fade=t=out:st={de-0.22}:d=0.22:color=0x0E1F48,format=yuv420p[v]")
    subprocess.run([FF,"-y","-loglevel","error"]+ins+
      ["-f","lavfi","-t",str(de),"-i","anullsrc=r=48000:cl=stereo",
       "-filter_complex",";".join(fl),"-map","[v]","-map",f"{len(layers)+1}:a",
       "-c:v","libx264","-crf","17","-preset","fast","-pix_fmt","yuv420p",
       "-c:a","aac","-shortest",f"seg/{idx:03d}.mp4"],check=True)
    card_idxs.append(idx)
def phrases(a,b):
    ws=[(s,e) for s,e,w in words if a-0.01<=s<b+0.01]
    if not ws: return []
    ph=[]; ps=ws[0][0]; pe=ws[0][1]
    for s,e in ws[1:]:
        if s-pe>=GAPTHR: ph.append((ps,pe)); ps=s
        pe=e
    ph.append((ps,pe))
    return [(max(a,s-PAD),min(b,e+TAIL)) for s,e in ph]
def play(a,b):
    for ps,pe in phrases(a,b):
        c=ps
        while pe-c>SUBLEN:
            c2=min(pe-0.4,c+SUBLEN-0.8); enc_her(c,c2-c); c=c2
        if pe-c>0.18: enc_her(c,pe-c)
enc_card("end.png",INTRO)
for act in ACTS:
    music_marks[act["name"]]=out_t
    for ht,txt in act["heads"]: heads.append((ht,txt))
    cur=act["s"]
    for clip,bs,bd in sorted(act["broll"],key=lambda b:b[1]):
        play(cur,bs); enc_broll(clip,bd,bs); cur=bs+bd
    play(cur,act["e"])
    if act["name"] in CARDS_AFTER: enc_card(f'{CARDS_AFTER[act["name"]]}.png',CARDD+0.4)
music_marks["end"]=out_t
# NOTE: no built end card — the approved Drive outro (LLA_Outro_Card.mp4) is appended as-is post-encode
def dipfade(k,mode):
    fn=f"seg/{k:03d}.mp4"
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",fn],capture_output=True,text=True).stdout)
    vf=(f"fade=t=out:st={max(0,d-0.16)}:d=0.16:color=0x0E1F48" if mode=="out" else "fade=t=in:d=0.16:color=0x0E1F48")
    subprocess.run([FF,"-y","-loglevel","error","-i",fn,"-vf",vf,"-c:v","libx264","-crf","17","-preset","fast","-pix_fmt","yuv420p","-c:a","copy","tmpseg.mp4"],check=True)
    os.replace("tmpseg.mp4",fn)
for c in card_idxs:
    if c-1>=1: dipfade(c-1,"out")
    if c+1<=idx: dipfade(c+1,"in")
with open("list.txt","w") as f:
    for k in range(1,idx+1): f.write(f"file 'seg/{k:03d}.mp4'\n")
subprocess.run([FF,"-y","-loglevel","error","-f","concat","-safe","0","-i","list.txt","-c","copy","cut.mp4"],check=True)
real=[]
for k in range(1,idx+1):
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"seg/{k:03d}.mp4"],capture_output=True,text=True).stdout)
    real.append(d)
pcum=[0.0]; rcum=[0.0]
for p,r in zip(PLAN,real): pcum.append(pcum[-1]+p); rcum.append(rcum[-1]+r)
def remap(t):
    i=max(0,bisect.bisect_right(pcum,t)-1); i=min(i,len(real)-1)
    return rcum[i]+min(max(0.0,t-pcum[i]), real[i])
print("plan total",round(pcum[-1],2),"real total",round(rcum[-1],2),"drift",round(rcum[-1]-pcum[-1],2))
def src2out(t):
    for s,e,o in SEG:
        if s<=t<=e: return o+(t-s)
    for s,e,o in SEG:
        if s-0.25<=t<=e+0.25: return o+(t-s)
    return None
HILITE={"direct","path","six","pillars","18","14","blueprint","class","session","seat","courtney","longevity","academy","harvard"}
BLUE=r"{\c&HFF6E00&}"; WHITE=r"{\c&HFFFFFF&}"
lines=[]; cur=[]; t0=None; last_e=0.0
for s,e,wd in words:
    o=src2out(s)
    if o is None:
        if cur: lines.append((t0,last_e,cur)); cur=[]; t0=None
        continue
    if t0 is None: t0=o
    cur.append(wd); last_e=src2out(e) or (o+0.4)
    if (wd and wd[-1] in ".!?") or (wd and wd[-1] in ",;" and len(cur)>=2) or len(cur)>=6:
        lines.append((t0,last_e,cur)); cur=[]; t0=None
if cur: lines.append((t0,last_e,cur))
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
ass=("[Script Info]\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\n"
  "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
  "Style: Cap,Inter,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H98000000,0,0,0,0,100,100,0.2,0,1,0,2.2,2,90,90,205,1\n"
  "Style: Head,Fraunces,72,&H00EAF2F5,&H00EAF2F5,&H30341608,&H30341608,0,0,0,0,100,100,9,0,3,13,0,8,60,60,42,1\n\n"
  "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
sent=True
for st,en,ws in lines:
    txt=" ".join((BLUE+w+WHITE) if w.strip(".,!?;").lower() in HILITE else w for w in ws)
    cap=txt[0].upper()+txt[1:] if sent and txt and txt[0].isalpha() else txt
    sent=bool(ws and ws[-1] and ws[-1][-1] in ".!?")
    rs,re=remap(st),remap(en)
    ass+=f"Dialogue: 0,{ts(rs)},{ts(max(re,rs+0.7))},Cap,,0,0,0,,{{\\fad(110,90)}}{cap}\n"
for ht,txt in heads:
    o=src2out(ht)
    if o is None: continue
    rh=remap(o)
    ass+=f"Dialogue: 1,{ts(rh)},{ts(rh+3.0)},Head,,0,0,0,,{{\\fad(380,380)\\fsp7\\t(0,600,\\fsp10)}}{txt}\n"
open("caps.ass","w").write(ass)
json.dump({k:remap(v) for k,v in music_marks.items()}, open("marks.json","w"))
print("segments:",idx,"out:",round(out_t,1),"caps:",len(lines),"dur:",round(rcum[-1],1))
