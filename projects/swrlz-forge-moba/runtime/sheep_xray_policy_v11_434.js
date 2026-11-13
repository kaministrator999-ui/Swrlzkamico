/* SE434_SHEEP_XRAY_POLICY_START */
const se434Xray={suppressedTeammateChecks:0};
function se434XrayEligible(unit,s){
 if(!renderer.xr?.isPresenting||!s||s.buildings.length<16||
    performancePrefs?.preset==='high')return true;
 const important=unit.id===s.controlledId||unit.id===s.selectedId;
 if(!important)se434Xray.suppressedTeammateChecks++;
 return important;
}
window.SWYRL_ENGINE_SHEEP_XRAY_434=Object.freeze({diagnose:()=>({
 ...se434Xray,policy:'busy immersive auto/low/medium: controlled and selected sheep; high: full teammate overlays',
 nativeModelsAndTeamMinimapUnchanged:true,cachedXRViewUsed:true
})});
/* SE434_SHEEP_XRAY_POLICY_END */
