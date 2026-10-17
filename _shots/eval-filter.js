const btn = document.querySelector('#filterBar .fbtn[data-t="九号两项硬核技术亮相苏超赛场"]');
if (!btn) return { error: 'filter button not found' };
btn.click();
await new Promise(r => setTimeout(r, 500));
const firstRow = document.querySelector('#rtable tbody tr');
const kpiVal = document.querySelector('#kpis .kpi:nth-child(3) .val');
return {
  activeBtn: document.querySelector('#filterBar .fbtn.on').textContent,
  firstRowStore: firstRow ? firstRow.querySelector('.s-name').textContent : 'none',
  firstRowSpread: firstRow ? firstRow.querySelectorAll('td')[6].textContent : 'none',
  hint: document.getElementById('rankHint').textContent.slice(0, 40),
  kpiRecords: kpiVal ? kpiVal.textContent : 'none'
};
