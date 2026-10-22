// Existing saves with the previous twenty-minute default adopt seven minutes.
// Explicitly tuned durations remain editable in the normal match rules.
const stSevenMinuteRulesBase=stCleanRules;
stCleanRules=function(value={}){return stSevenMinuteRulesBase({...value,...(Number(value.duration)===1200?{duration:420}:{})});};
