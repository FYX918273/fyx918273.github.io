import pandas as pd, json

files = [
    ('6k跑单神车选哪款', '6k跑单神车选哪款20261017135010.xlsx'),
    ('九号两项硬核技术亮相苏超赛场', '九号两项硬核技术亮相苏超赛场20261017134956.xlsx'),
    ('M5系列追加优惠', 'M5系列追加优惠20261017134926.xlsx'),
]

DISPLAY = {
    '天津市和平区多伦道九号电动车':'多伦道店','九号智能电动车（瑞景鞋城店）夏夏夏':'瑞景鞋城店',
    '九号泗水道店':'泗水道店','九号红旗南路店':'红旗南路店','五金城九号店':'五金城店',
    '冯贵全':'于台店','空港店':'空港店','派电建邦时代汇店':'派电建邦时代汇店',
    '天津东丽昆仑路九号店戴光宏':'昆仑路店','天津东丽湖九号店':'东丽湖店',
    '天津九号范宇轩':'城市运营中心','天津华明九号店王启航':'华明裕和路店',
    '天津市东丽区津塘公路（张贵庄）九号店':'张贵庄店','天津市九号丁字沽店高峰':'丁字沽店',
    '天津市九号利民道店张艳召':'利民道店','天津市北辰区双街九号店':'双街店',
    '天津市宁河区商业道九号店曾丽娜':'宁河商业道店','天津市河东区六纬路九号店张昆鹏':'六纬路店',
    '天津市滨海新区万达广场九号店':'滨海万达店','天津市滨海新区吾悦广场九号店':'吾悦广场店',
    '天津市西青区九号精武镇店薛米兰':'精武镇店','天津市鞍山西道九号店牛党徽':'鞍山西道店',
    '天津杨楼九号店':'杨楼店','天津河北月牙河岷江路九号':'岷江路店','尖山路九号':'尖山路店',
    '常贺敏':'杨柳青店','延吉道九号':'延吉道店','张永智':'宜兴埠店','张珊珊':'都市桃源店',
    '月牙河九号赵沽里店':'赵沽里店','李亚辉':'五马路店','牛启超':'吴家窑店','辛庄九号':'辛庄店',
    '大港九号电动车':'大港店','天津市红桥区咸阳路九号店':'咸阳路店',
}

def num(v):
    if v is None or pd.isna(v): return 0
    if isinstance(v, str):
        v = v.replace('%','').replace(',','').strip()
        if v == '' or v == '-': return 0
        return float(v)
    return float(v)

def store_key(operator, nickname):
    if pd.isna(operator) or str(operator)=='nan' or operator=='':
        return str(nickname)
    op = str(operator)
    if op == '吴红云':
        return '空港店' if '空港' in str(nickname) else '派电建邦时代汇店'
    return op

def disp(key): return DISPLAY.get(key, key)

all_rows = []
for task, f in files:
    a = pd.read_excel(f, sheet_name='账号完成情况')
    for _, r in a.iterrows():
        key = store_key(r['运营人'], r['账号昵称'])
        all_rows.append({
            'task': task, 'platform': r['平台'], 'nickname': r['账号昵称'],
            'key': key, 'store': disp(key),
            'status': r['任务情况'],
            'works': int(num(r['作品数'])), 'spread': int(num(r['传播总量'])),
            'interact': int(num(r['互动总量'])), 'likes': int(num(r['获赞总量'])),
        })
df = pd.DataFrame(all_rows)
stores = sorted(df['store'].unique())
ME = '多伦道店'

def agg(sub):
    return {
        'accounts': int(sub[['platform','nickname']].drop_duplicates().shape[0]),
        'done': int((sub['status']=='已完成').sum()), 'total': int(len(sub)),
        'rate': round((sub['status']=='已完成').sum()/len(sub)*100,1) if len(sub) else 0,
        'works': int(sub['works'].sum()), 'spread': int(sub['spread'].sum()),
        'interact': int(sub['interact'].sum()), 'likes': int(sub['likes'].sum()),
    }

store_summary = [{'store': s, **agg(df[df['store']==s])} for s in stores]
store_summary.sort(key=lambda x:(-x['spread'], -x['works'], -x['rate']))

task_store = {}
for task, _ in files:
    task_store[task] = {s: agg(df[(df['store']==s)&(df['task']==task)]) for s in stores}

plat_sum = {}
for p in ['抖音','快手','小红书','视频号']:
    plat_sum[p] = agg(df[df['platform']==p])

team_data = []
for task, f in files:
    st = pd.read_excel(f, sheet_name='团队数据')
    st = st[st['团队名称']=='天津市'].iloc[0]
    team_data.append({'task':task,'total':int(st['执行任务总账号数']),'done':int(st['已完成任务账号数']),
        'rate':num(st['完成率']),'works':int(st['作品数']),'spread':int(st['传播总量']),
        'interact':int(st['互动总量']),'likes':int(num(st['获赞总量']))})

works = []
for task, f in files:
    w = pd.read_excel(f, sheet_name='作品数据')
    for _, r in w.iterrows():
        works.append({'task':task,'platform':r['平台'],'type':r['类型'],'title':str(r['作品标题']),
            'link':str(r['作品链接']),'pub_time':str(r['发布时间']),'account':str(r['发布账号']),
            'plays':int(num(r['预估播放数/阅读数'])),'interact':int(num(r['互动量'])),
            'likes':int(num(r['获赞数'])),'comments':int(num(r['评论数']))})
acct_store = {(r[0], r[1]): r[2] for r in df[['platform','nickname','store']].drop_duplicates().values}
for wk in works:
    wk['store'] = acct_store.get((wk['platform'], wk['account']), '')
works.sort(key=lambda x:-x['plays'])

def rank_of(keyfn, store=ME):
    order = sorted(store_summary, key=keyfn)
    return [i+1 for i,x in enumerate(order) if x['store']==store][0]

me = {'store':ME,
      'rank_spread':rank_of(lambda x:(-x['spread'],-x['works'],-x['rate'])),
      'rank_works':rank_of(lambda x:(-x['works'],-x['spread'],-x['rate'])),
      'rank_rate':rank_of(lambda x:(-x['rate'],-x['spread'],-x['works']))}

kpi = agg(df)
kpi['stores'] = len(stores); kpi['accounts'] = int(df[['platform','nickname']].drop_duplicates().shape[0])
kpi['records'] = int(kpi['total'])

# 任务×平台×门店 完成矩阵（matrix[store][task][platform] = agg）
PLATS = ['抖音','快手','小红书','视频号']
matrix = {}
for s in stores:
    matrix[s] = {}
    for task, _ in files:
        sub = df[(df['store']==s)&(df['task']==task)]
        matrix[s][task] = {p: agg(sub[sub['platform']==p]) for p in PLATS if len(sub[sub['platform']==p])>0}

# 账号明细（门店详情页）：store -> [{platform, nickname, tasks:{task: 状态}}]
accts = {}
for s in stores:
    sub = df[df['store']==s]
    accts[s] = []
    for (platform, nickname), g in sub.groupby(['platform','nickname']):
        accts[s].append({'platform':platform,'nickname':nickname,
            'tasks':{r['task']: r['status'] for _, r in g.iterrows()}})

out = {'kpi':kpi,'stores':store_summary,'task_store':task_store,'plat_sum':plat_sum,
       'team':team_data,'works':works,'me':me,'matrix':matrix,'accts':accts}
with open('/Users/fanyuxuan/Doubao/chats/2026-10-17/new-chat/kos-dashboard/data.json','w') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print('KPI:', json.dumps(kpi, ensure_ascii=False))
print('ME:', json.dumps(me, ensure_ascii=False))
print('平台:', json.dumps(plat_sum, ensure_ascii=False))
print('Top5(传播):')
for x in store_summary[:5]: print(' ', x['store'], x['accounts'],'账号',x['rate'],'%',x['works'],'作品',x['spread'],'传播')
print('Bottom3(传播):')
for x in store_summary[-3:]: print(' ', x['store'], x['accounts'],'账号',x['rate'],'%',x['works'],'作品',x['spread'],'传播')
print('作品Top3:')
for w in works[:3]: print(' ', w['store'], w['task'][:10], w['platform'], w['plays'], w['title'][:20])
