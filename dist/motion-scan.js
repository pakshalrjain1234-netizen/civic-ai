// Pure scan helpers shared by the browser and the regression checks.
(function(root){
  function overlap(a,b){
    if(!a||!b)return 0;
    const w=Math.max(0,Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x));
    const h=Math.max(0,Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y));
    return w*h/Math.max(1e-9,a.width*a.height+b.width*b.height-w*h);
  }
  function sharpness(rgba,width,height){
    // Laplacian variance on a tiny thumbnail, excluding its border.
    const gray=new Float32Array(width*height);
    for(let i=0;i<gray.length;i++)gray[i]=.299*rgba[i*4]+.587*rgba[i*4+1]+.114*rgba[i*4+2];
    let sum=0,squares=0,count=0;
    for(let y=1;y<height-1;y++)for(let x=1;x<width-1;x++){
      const i=y*width+x,v=4*gray[i]-gray[i-1]-gray[i+1]-gray[i-width]-gray[i+width];
      sum+=v;squares+=v*v;count++;
    }
    return count?Math.max(0,squares/count-(sum/count)**2):0;
  }
  class Stabilizer{
    constructor(){this.reset();}
    reset(){this.pending=[];this.visible=[];this.expires=0;}
    update(detections,time){
      const confirmed=detections.filter(d=>d.confidence===null||d.confidence>=.65||this.pending.some(p=>
        time-p.time<=1200&&p.d.class===d.class&&overlap(p.d.bbox,d.bbox)>=.15));
      this.pending=detections.map(d=>({d,time}));
      if(confirmed.length){this.visible=confirmed;this.expires=time+900;return {fresh:confirmed,display:confirmed};}
      // A different observed class invalidates a stale overlay immediately.
      if(detections.length&&this.visible.some(v=>!detections.some(d=>d.class===v.class)))this.visible=[];
      if(time>=this.expires)this.visible=[];
      return {fresh:[],display:this.visible.map(d=>({...d,stale:true}))};
    }
    expire(time){if(time>=this.expires)this.visible=[];return this.visible;}
  }
  function nextDelay(elapsed,failed=false){
    // Start-to-start opportunity of 300 ms, with a quiet gap after slow requests.
    return failed?1000:Math.max(80,300-elapsed);
  }
  root.CivicMotion={sharpness,Stabilizer,nextDelay};
})(globalThis);
