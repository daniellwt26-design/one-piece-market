# 海賊王日本卡價情報 PWA

## 手機一按即看
部署到 GitHub Pages 後，用手機開網址：
- iPhone Safari：分享 > 加入主畫面
- Android Chrome：選單 > 加到主畫面 / 安裝應用程式

## 部署步驟
1. 建立 GitHub repository，把本資料夾內所有檔案上傳，必須保留 `.github/workflows/update.yml`。
2. 到 Actions，執行 `Refresh Japan market data` 一次。
3. 到 Settings > Pages，選 Deploy from a branch，設定 main / root。
4. GitHub Pages網址生成後，在手機加入主畫面。

## 更新安排
GitHub Actions 每日香港時間約 08:15、14:15、20:15 嘗試更新，實際執行可能延遲。

## 重要限制
- 資料來源：SNKRDUNK文章、Card Rush收購表、遊々亭收購表。
- 網站改版、反爬措施、robots或使用條款可能令來源失效。請按來源狀態判斷可用性。
- 收購價、零售價及成交價不可互相當作同一價格。
- 目前SNKRDUNK設定為一篇示範市場文章，不代表全站所有卡。要擴充覆蓋率，可在`sources.json`加入更多卡牌文章URL。
- 系統不會在缺乏歷史價格及跨來源匹配時製造升跌或買入結論。
