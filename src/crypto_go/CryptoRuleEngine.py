import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

CRYPTO_DICT = {
    # 格式: {标准化符号: [匹配模式列表]}
    "BTC": ["\\bBTC\\b", "\\bbitcoin\\b", "\\bxbt\\b", "₿"],
    "ETH": ["\\bETH\\b", "\\bethereum\\b", "Ξ"],
    "SOL": ["\\bSOL\\b", "\\bsolana\\b"],
    "XRP": ["\\bXRP\\b", "\\bripple\\b"],
    "DOGE": ["\\bDOGE\\b", "\\bdogecoin\\b", "\\bdoge\\b"],
    "SHIB": ["\\bSHIB\\b", "\\bshiba\\b", "\\bshib\\b"],
    # ... 扩展至 Top 50 币种（约 200 个条目）
}

# 金融情绪关键词（增强 VADER）
BULLISH_WORDS = ["moon", "🚀", "bull", "pump", "ath", "lambo", "tothemoon", "diamond hands"]
BEARISH_WORDS = ["dump", "📉", "bear", "crash", "rekt", "paper hands", "fud", "capitulate"]

class CryptoRuleEngine:
    def __init__(self):
        self.crypto_dict = CRYPTO_DICT
        self.vader = SentimentIntensityAnalyzer()
        # 增强 VADER 词典
        for word in BULLISH_WORDS: self.vader.lexicon[word] = 2.0
        for word in BEARISH_WORDS: self.vader.lexicon[word] = -2.0

    def extract_coins(self, text):
        coins = set()
        for coin, patterns in self.crypto_dict.items():
            if any(re.search(p, text, re.IGNORECASE) for p in patterns):
                coins.add(coin)
        return list(coins)

    def calculate_sentiment(self, text):
        coins = self.extract_coins(text)
        # 基础 VADER 分数
        base_score = self.vader.polarity_scores(text)["compound"]

        # 增强：检测币种专属上下文（滑动窗口 15 词）
        coin_sentiments = {}
        words = text.lower().split()
        for coin in coins:
            # 查找币种位置
            positions = [i for i, w in enumerate(words)
                         if any(re.search(p, w, re.IGNORECASE) for p in self.crypto_dict[coin])]
            if not positions:
                coin_sentiments[coin] = base_score
                continue

            # 提取上下文窗口
            contexts = []
            for pos in positions:
                start = max(0, pos - 15)
                end = min(len(words), pos + 15)
                contexts.append(" ".join(words[start:end]))

            # 计算上下文情绪
            ctx_scores = [self.vader.polarity_scores(ctx)["compound"] for ctx in contexts]
            coin_sentiments[coin] = sum(ctx_scores) / len(ctx_scores) if ctx_scores else base_score

        # 置信度 = |情绪分数| + 提及频率加成
        confidence = abs(base_score) * 0.7 + (len(coins) > 0) * 0.3
        return coin_sentiments, confidence
