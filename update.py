import json,re,time,datetime,pathlib,statistics
import requests
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).parent
HEAD={'User-Agent':'Mozilla/5.0 (compatible; OPCGMarketMonitor/1.0; +personal dashboard)','Accept-Language':'ja,en;q=0.8'}
CARD=re.compile(r'((?:OP|EB|ST|P)-?\d{2}-\d{3}|(?:OP|EB|ST)\d{2}-\d{3})',re.I)
YEN=re.compile(r'([0-9][0-9,]*)\s*円')

def get(url):
 r=requests.get(url,headers=HEAD,timeout=30);r.raise_for_status();return r.text

def rows_from_text(text,source,kind):
 text=' '.join(text.split()); matches=list(CARD.finditer(text)); out=[]
 for i,m in enumerate(matches):
  seg=text[m.start():matches[i+1].start() if i+1<len(matches) else min(len(text),m.start()+260)]
  prices=[int(x.replace(',','')) for x in YEN.findall(seg)]
  if not prices: continue
  name=seg[len(m.group(0)):].strip(' []-/')[:90]
  name=re.split(r'\s(?:SR|SEC|L|P-SR|P-SEC|Card List)\s',name)[0][:65]
  out.append({'card_id':m.group(0).upper().replace('OP0','OP0'),'name':name or m.group(0),'source':source,'kind':kind,'prices_jpy':prices[:3]})
 return out

def parse_source(s):
 try:
  html=get(s['url']); soup=BeautifulSoup(html,'html.parser')
  for x in soup(['script','style','noscript']): x.decompose()
  rows=rows_from_text(soup.get_text(' ',strip=True),s['name'],s['type'])
  return {'id':s['id'],'name':s['name'],'url':s['url'],'ok':True,'records':rows[:350],'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 except Exception as e:
  return {'id':s['id'],'name':s['name'],'url':s['url'],'ok':False,'error':str(e)[:180],'records':[]}

def combine(srcs):
 by={}
 for s in srcs:
  for r in s['records']:
   k=r['card_id']; by.setdefault(k,{'card_id':k,'name':r['name'],'sources':{},'all':[]})
   p=r['prices_jpy'][0];by[k]['sources'][s['id']]=p;by[k]['all'].append(p)
 out=[]
 for v in by.values():
  vals=v.pop('all');v['median_jpy']=round(statistics.median(vals));v['source_count']=len(v['sources'])
  buys=[p for k,p in v['sources'].items() if k in ('cardrush','yuyutei')]
  market=v['sources'].get('snkrdunk')
  v['buy_median_jpy']=round(statistics.median(buys)) if buys else None;v['market_jpy']=market
  v['spread_pct']=round((market-v['buy_median_jpy'])/market*100,1) if market and v['buy_median_jpy'] else None
  score=35+min(v['source_count'],3)*12
  if v['spread_pct'] is not None: score += 18 if 10<=v['spread_pct']<=35 else 6 if 0<v['spread_pct']<55 else -12
  v['confidence']='高' if v['source_count']>=3 else '中' if v['source_count']==2 else '低';v['score']=max(0,min(100,score))
  v['signal']='觀察' if v['source_count']>=2 else '資料不足'
  out.append(v)
 return sorted(out,key=lambda x:(x['source_count'],x['score'],x['median_jpy']),reverse=True)

def main():
 cfg=json.loads((ROOT/'sources.json').read_text());src=[]
 for s in cfg['sources']: src.append(parse_source(s));time.sleep(2)
 cards=combine(src); ok=sum(x['ok'] for x in src)
 result={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':src,'cards':cards,'summary':{'sources_ok':ok,'cards':len(cards),'multi_source':sum(x['source_count']>=2 for x in cards)},'notice':'網站結構、存取限制或條款改動可令擷取中斷；只顯示可核對來源，單一來源不會產生買入建議。'}
 (ROOT/'data.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
if __name__=='__main__': main()
