"""A truncated identity draft must retry before any accepted delivery.

This uses controlled completion receipts to check engine behavior; separate
pinned-GGUF workflow replay establishes real model quality.
"""
import sys
from unittest import mock
sys.modules.setdefault('huggingface_hub',mock.MagicMock())
sys.modules.setdefault('llama_cpp',mock.MagicMock())
import lfm2_700m_engine as engine

class TokenCounter:
    def tokenize(self,data,**kwargs):
        return data.split()

def replay(completions,payload):
    calls=[]
    def complete(model,messages,max_tokens,temperature):
        text,finish=completions[len(calls)]
        calls.append({'messages':messages,'maxTokens':max_tokens})
        return text,{'durationMs':1,'firstTokenLatencyMs':1,'deltaChunks':1,
                     'finishReason':finish,'requestedMaxTokens':max_tokens}
    with mock.patch.object(engine,'load',return_value=TokenCounter()),mock.patch.object(
            engine,'buffered_chat_completion',side_effect=complete):
        events=list(engine.generate_events(payload))
    return events,calls

payload={'prompt':'Who am I','history':[],'profile':'','userProfile':'',
         'programmingIntent':{'codingTask':False}}
events,calls=replay([
    ("I don't know your name yet",'length'),
    ("You haven't told me your name yet.",'stop'),
],payload)
attempts=[event['attempt'] for event in events if event['type']=='CANDIDATE_ATTEMPT']
assert len(attempts)==2 and not attempts[0]['accepted'] and attempts[1]['accepted']
assert 'model-output-token-limit' in attempts[0]['validationReasons']
assert calls[1]['maxTokens']>calls[0]['maxTokens']
assert calls[1]['maxTokens']<=192
assert len([message for message in calls[1]['messages'] if message['role']=='system'])==1
assert not any(event['type']=='FAILED' for event in events)
assert ''.join(event.get('text','') for event in events if event['type']=='DELTA')=="You haven't told me your name yet."

# A second truncated draft is still rejected even when its text names the gap.
events,calls=replay([
    ("I don't know your name yet",'length'),
    ("I don't know your name yet",'length'),
],payload)
attempts=[event['attempt'] for event in events if event['type']=='CANDIDATE_ATTEMPT']
assert len(attempts)==2 and not any(attempt['accepted'] for attempt in attempts)
assert any(event['type']=='FAILED' and event['reason']=='OUTPUT_TOKEN_LIMIT' for event in events)
assert not any(event['type']=='COMPLETED' for event in events)

# Missing-name calibration remains required when correcting an earlier reply.
followup={**payload,'prompt':'Are you sure about that?',
          'history':[{'role':'user','text':'Who am I'},
                     {'role':'assistant','text':'You are ASSISTANT.'}]}
events,calls=replay([
    ("You are a person.",'stop'),
    ("I don't know your name yet; my earlier answer was wrong.",'stop'),
],followup)
attempts=[event['attempt'] for event in events if event['type']=='CANDIDATE_ATTEMPT']
assert len(attempts)==2 and 'missing-unknown-user-name-calibration' in attempts[0]['validationReasons']
assert attempts[1]['accepted']
# Untrusted assistant names stay in the original record, but cannot become
# user-name evidence. The user's original question remains in model context.
assert any('Are you sure about that?' in message['content'] for message in calls[0]['messages'])
assert not any(message['content']=='You are ASSISTANT.' for message in calls[0]['messages'])
context=next(event for event in events if event['type']=='CONTEXT')
assert context['identityHistoryMessagesExcluded']==2
assert followup['history'][1]['text']=='You are ASSISTANT.'
# A new direct human name/correction overrides stale account evidence for this
# conversation. It stays a statement in the actual model USER message.
for current in ('Call me River','Actually my name is River'):
    naming={**followup,'prompt':current,'userProfile':'Name: Avery'}
    events,calls=replay([("Your name is River; I'll use River in this conversation.",'stop')],naming)
    attempts=[event['attempt'] for event in events if event['type']=='CANDIDATE_ATTEMPT']
    assert len(attempts)==1 and attempts[0]['accepted']
    assert calls[0]['messages'][-1]['content']==current
    assert 'Supported human name: River.' in calls[0]['messages'][0]['content']
    assert 'No supported personal name' not in calls[0]['messages'][0]['content']
    assert naming['userProfile']=='Name: Avery'
    # On the next turn the same account profile is still Avery, while the
    # explicit in-thread preference remains River. No profile write occurred.
    following={**naming,'prompt':'Who am I?',
               'history':list(naming['history'])+[
                   {'role':'user','text':current},
                   {'role':'assistant','text':"I'll refer to you as River."}]}
    events,calls=replay([("Your name is River.",'stop')],following)
    attempts=[event['attempt'] for event in events if event['type']=='CANDIDATE_ATTEMPT']
    assert len(attempts)==1 and attempts[0]['accepted']
    assert 'Supported human name: River.' in calls[0]['messages'][0]['content']
    assert following['userProfile']==naming['userProfile']=='Name: Avery'

print('Identity truncation retry, evidence ownership and follow-up calibration behavior PASS')
