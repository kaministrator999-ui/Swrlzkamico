// §E v11.223 · stronger anatomically layered fist + wrist-driven wave.
// The existing 17-bone rig and saved timeline format remain unchanged.
// Rotation keys below animate the parent wrist/palm, not a detached hand mesh.
function se223WavePose(rig,side,flutter=0){
 const pose=se221GesturePose(rig,'wave');
 const s=Math.max(-1,Math.min(1,side)),f=Math.max(-1,Math.min(1,flutter));
 // Z rolls the whole hand laterally around its wrist; Y twists its face
 // toward/away from viewer; X adds a subtle forward/backward wobble.
 pose.wrist=[-.04*s,.22*s,.31*s];
 pose.palm=[.028*f,.095*s,.065*s];
 for(const [i,name] of ['index','middle','ring','pinky'].entries()){
  const base=pose[name+'_mcp'];
  base[0]+=(.045+(i*.008))*f;
  pose[name+'_pip'][0]+=.055*f;
  pose[name+'_dip'][0]+=.025*f;
 }
 pose.thumb_cmc[1]+=.05*f;
 pose.thumb_mcp[2]+=.045*f;
 return pose;
}
function se223WaveTimeline(rig){
 // Multiple alternating directions — not the old Open→one static wave→Open.
 // Stored as ordinary joint keyframes, fully editable and JSON-exportable.
 const open=se221GesturePose(rig,'open');
 return [
  {time:0,pose:open},
  {time:.24,pose:se223WavePose(rig, .85,.35)},
  {time:.54,pose:se223WavePose(rig,-1,-.40)},
  {time:.86,pose:se223WavePose(rig, 1,.45)},
  {time:1.18,pose:se223WavePose(rig,-1,-.42)},
  {time:1.50,pose:se223WavePose(rig, 1,.33)},
  {time:1.84,pose:se223WavePose(rig,-.80,-.24)},
  {time:2.20,pose:open}
 ];
}
