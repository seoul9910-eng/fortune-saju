from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
from zoneinfo import ZoneInfo
import hashlib, random
from engine import get_chart, ELEM, ten_god, day_pillar, STEMS, BRANCHES

app = Flask(__name__)
SENSE = {
'비견': ('자기 기준이 분명하고 독립적으로 판단하는 힘','상대의 의견을 끝까지 듣지 않고 밀어붙이는 일'),
'겁재': ('승부욕과 추진력으로 경쟁 상황에 대응하는 힘','조급한 비교와 충동적인 결정'),
'식신': ('실력을 꾸준히 쌓고 결과를 만들어 내는 능력','편안함만 좇다가 기회를 놓치는 일'),
'상관': ('기존의 틀을 의심하고 표현하는 재능','말이 앞서서 불필요한 갈등을 만드는 일'),
'정재': ('계획적인 자원 관리와 안정적인 실행력','지나친 계산으로 새로운 가능성을 닫는 일'),
'편재': ('사람과 기회의 흐름을 읽는 유연한 감각','근거가 부족한 거래나 과감한 지출'),
'정관': ('원칙을 지키고 책임을 끝까지 감당하는 태도','남의 기대에 맞추느라 자신을 소진하는 일'),
'편관': ('압박 속에서 결단하고 난관을 돌파하는 기질','무리한 일정과 지나친 긴장'),
'정인': ('배움과 신뢰를 바탕으로 깊이를 쌓는 능력','준비만 오래 하다가 실행을 미루는 일'),
'편인': ('독창적인 관점과 깊이 있는 탐구 능력','생각이 복잡해져 현실적인 기회를 놓치는 일')}
TOPICS = {
'총운':('전체적인 일의 우선순위','오늘 해야 할 일을 세 가지로 줄여 가장 중요한 것부터 끝내 봐'),
'금전운':('수입과 지출, 계약과 소비의 균형','계약과 지출은 숫자와 조건을 직접 확인해'),
'애정운':('감정 표현과 가까운 관계의 온도','상대의 말을 추측하지 말고 차분히 물어봐'),
'직업운':('업무의 책임과 성과, 협업의 흐름','마감과 역할을 명확히 정하고 한 가지 성과를 남겨'),
'대인관계운':('가족과 친구, 동료 사이의 소통','말의 속도를 낮추고 상대의 관점을 확인해'),
'건강운':('생활 리듬과 휴식의 균형','무리한 일정을 줄이고 규칙적으로 쉬어')}

def format_topic(topic, chart, flow_ten, period, pillar_label):
    day=chart['day']; base=chart['pillars'][1]['branchTen']
    strength, risk=SENSE[base]; flow_strength, flow_risk=SENSE[flow_ten]
    domain, action=TOPICS[topic]
    return (f'【{topic}】 {period}의 흐름을 사주명리학의 상징으로 읽어 볼게. 너의 일간은 {day[0]}({ELEM[day[0]]})이고, '
            f'일지 본기의 십성은 {base}야. 이 구성에서는 {strength}이 중요한 특징으로 해석돼. '
            f'{pillar_label}의 천간은 일간을 기준으로 {flow_ten}에 해당해. 전통적으로 이는 {flow_strength}과 연결해 풀이하지. '
            f'따라서 {domain}을 살필 때, 원래의 기질과 시기의 흐름을 함께 생각하는 게 좋아. '
            f'오행의 겉으로 드러난 분포는 {", ".join(f"{k} {v}개" for k,v in chart["counts"].items())}야. '
            f'이 숫자는 여덟 글자의 단순 개수이지, 계절의 힘과 지장간까지 반영한 신강·신약 판정은 아니야. '
            f'너의 장점인 {strength}을 살리되 {risk}은 조심해야 해. '
            f'특히 {flow_risk}에 주의를 기울여. 실천할 일은 분명해. {action}. '
            '운세는 결과를 보장하는 예언이 아니라, 스스로의 선택을 점검하는 전통적 해석이라는 점도 기억해.')

@app.get('/')
def home(): return render_template('index.html')

@app.post('/api/chart')
def chart():
    try:
        d=request.get_json(silent=True)
        if not isinstance(d,dict): raise ValueError('입력 형식을 확인해 주세요.')
        c=get_chart(d)
        name=str(d.get('name') or '방문자').strip()[:30]
        day=c['day']; daystem=day[0]; base=c['pillars'][1]['branchTen']; month_ten=c['pillars'][2]['ten']
        strength,risk=SENSE[base]; mstrength,mrisk=SENSE[month_ten]
        counts=c['counts']; strong=max(counts,key=counts.get)
        c['name']=name
        c['personality']=(f'너의 일간은 {daystem}({ELEM[daystem]})이고 일지 본기의 십성은 {base}야. '
            f'전통 명리학에서는 이 조합을 {strength}과 연결해 풀이해. '
            f'월간에 놓인 {month_ten}은 {mstrength}을 보태는 요소로 해석하지. '
            f'겉으로 드러난 오행에서는 {strong}이 상대적으로 많아. '
            f'다만 {risk}과 {mrisk}은 경계하는 게 좋아. '
            '너의 재물 감각이나 인간관계도 한 가지 십성만으로 단정할 수는 없어. '
            '사주는 스스로의 강점과 선택을 돌아보는 전통적 참고 자료로 활용해.')
        if c['luck']:
            lines=[f"{p['startAge']}~{p['endAge']}세: {p['pillar']} 대운 · 천간 십성 {p['ten']}. {SENSE[p['ten']][0]}을 이 시기의 상징적인 주제로 읽어." for p in c['luck']]
            c['lifetime']='\n'.join(lines)+'\n'+c['luckNote']
        else: c['lifetime']=c['luckNote']
        today=datetime.now(ZoneInfo('Asia/Seoul')).date()
        today_pillar=day_pillar(today)
        today_ten=ten_god(daystem,today_pillar[0]); today_strength,today_risk=SENSE[today_ten]
        c['daily']=(f'{today:%Y년 %m월 %d일}의 일진은 {today_pillar}이고, 네 일간 {daystem}을 기준으로 오늘의 천간은 {today_ten}이야.\n'
          f'{today_strength}을 살릴 수 있는 하루로 풀이해.\n'
          f'중요한 약속과 지출은 한 번 더 확인하고, {today_risk}은 꼭 피하도록 해.\n'
          '이 해석은 전통 명리학에 근거한 참고이며 미래를 확정하지 않아.')
        c['todayPillar']=today_pillar
        c['dailyTopics']={topic:format_topic(topic,c,today_ten,'오늘',f'오늘의 일진 {today_pillar}') for topic in TOPICS}
        # Year pillar based on Li Chun boundary. This is the year of the current KST date.
        year=today.year
        target_year=year
        annual_pillar=STEMS[(target_year-4)%10]+BRANCHES[(target_year-4)%12]
        annual_ten=ten_god(daystem,annual_pillar[0])
        c['annualPillar']=annual_pillar
        c['annualTopics']={topic:format_topic(topic,c,annual_ten,f'{target_year}년',f'{target_year}년 입춘 이후 세운 {annual_pillar}') for topic in TOPICS}
        seed=hashlib.sha256(f'{c["solar"]}|{d.get("hour")}|{today.isoformat()}'.encode()).digest()
        c['numbers']=sorted(random.Random(int.from_bytes(seed,'big')).sample(range(1,46),6))
        c['notes']=[f"계산 기준: {c['rule']}",f"입춘: {c['lichun']}",f"현재 월주 절기 구간: {c['prevJie']} ~ {c['nextJie']}",c['noble']['rule'],c['luckNote'],'음양력 변환: korean-lunar-calendar · 절기: Swiss Ephemeris. 모든 날짜·학파별 독립 만세력 교차검증은 완료되지 않았습니다.']
        return jsonify(c)
    except (ValueError,TypeError,OverflowError,KeyError) as exc:return jsonify({'error':str(exc)}),400

@app.get('/health')
def health():return jsonify({'ok':True,'engine':'solar-terms','access':'free'})

if __name__=='__main__':app.run(host='127.0.0.1',port=5000,debug=False)
