import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime

try:
    import nest_asyncio
    nest_asyncio.apply()
    print("✅ nest_asyncio применен для ESOLLL AI Professional Analytics Engine")
except ImportError:
    print("⚠️ Установите: pip install nest-asyncio")

class EsolllAIAnalyzer:
    def __init__(self, anthropic_api_key):
        self.anthropic_api_key = anthropic_api_key
        self.ai_headers = {
            'Content-Type': 'application/json',
            'x-api-key': anthropic_api_key,
            'anthropic-version': '2023-06-01'
        }
        self.problems_by_category = {
            "одежда": {
                "Размеры": ["размер", "маленький", "большой", "не подошел", "размерная сетка"],
                "Качество ткани": ["ткань", "линяет", "растягивается", "рвется", "тонкая"],
                "Швы": ["швы", "нитки", "расползается", "кривые швы"],
            },
            "электроника": {
                "Поломка": ["сломался", "не работает", "перегорел", "сгорел"],
                "Батарея": ["не заряжается", "батарея", "разряжается", "быстро садится"],
                "Совместимость": ["не подходит", "не совместим"],
                "Качество сборки": ["хрупкий", "дешевый", "пластик плохой"],
            },
            "default": {
                "Качество": ["дешевый", "хрупкий", "некачественный", "плохой"],
                "Функциональность": ["не работает", "бракованный", "глючит"],
                "Безопасность": ["опасно", "острые края", "токсичный запах"],
                "Упаковка": ["плохая упаковка", "повреждена", "помят"],
                "Запах": ["запах", "воняет", "химический запах"],
            }
        }
    
    async def analyze_with_esolll_ai(self, reviews, product_name, basic_analysis):
        """🤖 ESOLLL AI PROFESSIONAL ANALYSIS ENGINE"""
        try:
            # Подготавливаем данные для ESOLLL AI
            reviews_sample = []
            for review in reviews[:25]:  # Берем 25 лучших отзывов для AI
                text = review.get('review_text', review.get('text', ''))
                rating = review.get('rating', review.get('review_rating', 5))
                if text and len(text.strip()) > 20:
                    reviews_sample.append({
                        'text': text[:600],  # Увеличили лимит
                        'rating': rating,
                        'date': review.get('date', '')
                    })
            
            # Промпт для ESOLLL AI Professional Engine
            ai_prompt = f"""Ты профессиональный аналитик ESOLLL AI Professional Analytics Engine для анализа товаров электронной коммерции.

ТОВАР: {product_name}

ОТЗЫВЫ ПОКУПАТЕЛЕЙ:
{json.dumps(reviews_sample, ensure_ascii=False, indent=2)}

БАЗОВАЯ СТАТИСТИКА:
- Всего отзывов: {basic_analysis.get('total_reviews', 0)}
- Русских отзывов: {basic_analysis.get('russian_reviews', 0)}
- Критических: {basic_analysis.get('critical_reviews_count', 0)}

ЗАДАЧИ ESOLLL AI:
1. Выполни глубокий семантический анализ отзывов
2. Выяви скрытые проблемы между строк
3. Определи эмоциональный профиль покупателей
4. Составь ТОП практические бизнес-рекомендации
5. Дай профессиональный прогноз развития

ФОРМАТ ОТВЕТА (строго JSON):
{{
    "esolll_ai_problems": [
        {{
            "name": "название проблемы",
            "description": "детальное описание проблемы",
            "severity": "критическая/высокая/средняя/низкая",
            "business_impact": "влияние на бизнес",
            "frequency_estimate": "примерный процент",
            "examples": ["конкретные примеры из отзывов"]
        }}
    ],
    "emotional_profile": {{
        "overall_mood": "позитивный/нейтральный/негативный/смешанный",
        "frustration_level": "уровень 1-10",
        "satisfaction_triggers": ["что радует покупателей"],
        "pain_triggers": ["что расстраивает покупателей"],
        "loyalty_risk": "риск потери лояльности клиентов"
    }},
    "professional_insights": {{
        "immediate_fixes": ["срочные исправления"],
        "strategic_improvements": ["стратегические улучшения"],
        "competitive_positioning": "позиция относительно конкурентов",
        "market_opportunities": ["возможности на рынке"],
        "critical_risks": ["критические риски бизнеса"]
    }},
    "esolll_predictions": {{
        "sales_trend": "прогноз продаж",
        "quality_trend": "тренд качества",
        "customer_retention": "удержание клиентов",
        "return_forecast": "прогноз возвратов",
        "improvement_timeline": "сроки улучшений"
    }},
    "esolll_score": {{
        "product_rating": "оценка товара 1-10",
        "buy_recommendation": "покупать/не_покупать/осторожно",
        "confidence": "уровень уверенности анализа",
        "risk_level": "низкий/средний/высокий/критический"
    }}
}}

Анализируй на РУССКОМ ЯЗЫКЕ как эксперт ESOLLL AI с максимальной практической пользой!"""

            # Отправляем в ESOLLL AI Engine
            async with aiohttp.ClientSession() as session:
                ai_url = "https://api.anthropic.com/v1/messages"
                ai_payload = {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4500,
                    "messages": [
                        {
                            "role": "user", 
                            "content": ai_prompt
                        }
                    ]
                }
                
                async with session.post(
                    ai_url, 
                    headers=self.ai_headers, 
                    json=ai_payload,
                    timeout=aiohttp.ClientTimeout(total=35)
                ) as response:
                    if response.status == 200:
                        ai_response = await response.json()
                        ai_content = ai_response['content'][0]['text']
                        
                        try:
                            # Извлекаем JSON из ответа ESOLLL AI
                            json_start = ai_content.find('{')
                            json_end = ai_content.rfind('}') + 1
                            json_str = ai_content[json_start:json_end]
                            esolll_analysis = json.loads(json_str)
                            
                            print("✅ ESOLLL AI PROFESSIONAL ANALYSIS COMPLETED!")
                            return esolll_analysis
                            
                        except json.JSONDecodeError as e:
                            print(f"⚠️ Ошибка парсинга ESOLLL AI: {e}")
                            print(f"AI ответ: {ai_content[:500]}...")
                            return self.create_fallback_analysis()
                    else:
                        print(f"❌ Ошибка ESOLLL AI Engine: {response.status}")
                        return self.create_fallback_analysis()
                        
        except Exception as e:
            print(f"❌ Ошибка ESOLLL AI Professional Engine: {e}")
            return self.create_fallback_analysis()
    
    def create_fallback_analysis(self):
        """Резервный анализ если ESOLLL AI недоступен"""
        return {
            "esolll_ai_problems": [
                {
                    "name": "Требуется дополнительный анализ",
                    "description": "ESOLLL AI Engine временно недоступен",
                    "severity": "средняя",
                    "business_impact": "Ограниченная аналитика",
                    "frequency_estimate": "неопределено",
                    "examples": ["Профессиональный анализ будет доступен после восстановления"]
                }
            ],
            "emotional_profile": {
                "overall_mood": "нейтральный",
                "frustration_level": "5",
                "satisfaction_triggers": ["Требуется AI анализ"],
                "pain_triggers": ["ESOLLL AI недоступен"],
                "loyalty_risk": "неопределен"
            },
            "professional_insights": {
                "immediate_fixes": ["Восстановить ESOLLL AI Engine"],
                "strategic_improvements": ["Использовать базовую аналитику"],
                "competitive_positioning": "Требует AI анализа",
                "market_opportunities": ["Определяется после AI анализа"],
                "critical_risks": ["Отсутствие профессиональной аналитики"]
            },
            "esolll_predictions": {
                "sales_trend": "Требует AI прогнозирования",
                "quality_trend": "Базовый анализ",
                "customer_retention": "Неопределен",
                "return_forecast": "Требует AI модели",
                "improvement_timeline": "Восстановить AI Engine"
            },
            "esolll_score": {
                "product_rating": "7",
                "buy_recommendation": "осторожно",
                "confidence": "низкий - нет AI анализа",
                "risk_level": "средний"
            }
        }
    
    def determine_category(self, product_name):
        text = product_name.lower()
        if any(word in text for word in ["одежда", "футболка", "джинсы", "платье", "брюки"]):
            return "одежда"
        elif any(word in text for word in ["электроника", "зарядка", "кабель", "наушники", "триммер"]):
            return "электроника"
        else:
            return "default"
    
    def filter_russian_reviews(self, reviews):
        russian_reviews = []
        for review in reviews:
            text = review.get('text', review.get('review_text', ''))
            if not text or len(text.strip()) < 15:
                continue
            
            russian_chars = sum(1 for char in text if 'а' <= char.lower() <= 'я')
            total_chars = sum(1 for char in text if char.isalpha())
            
            if total_chars > 0 and (russian_chars / total_chars) > 0.5:
                normalized_review = {
                    'review_text': text,
                    'text': text,
                    'rating': review.get('rating', review.get('valuation', 5)),
                    'review_rating': review.get('rating', review.get('valuation', 5)),
                    'date': review.get('date', ''),
                    'answer': review.get('answer', '')
                }
                russian_reviews.append(normalized_review)
        
        return russian_reviews
    
    async def analyze_with_esolll_professional(self, reviews, product_name):
        """🚀 ESOLLL AI PROFESSIONAL COMPREHENSIVE ANALYSIS"""
        russian_reviews = self.filter_russian_reviews(reviews)
        if not russian_reviews:
            return None
        
        category = self.determine_category(product_name)
        
        # Расширенный анализ проблем
        enhanced_problems = {
            "Размеры и габариты": ["размер", "маленький", "большой", "не подошел", "размерная сетка", "велик", "мал", "не тот размер"],
            "Качество материалов": ["качество", "дешевый", "хрупкий", "некачественный", "плохой", "ужасный", "материал", "пластик"],
            "Функциональность": ["не работает", "бракованный", "глючит", "сломался", "поломка", "брак", "дефект", "не функционирует"],
            "Энергопитание": ["батарея", "не заряжается", "разряжается", "быстро садится", "заряд", "зарядка", "питание"],
            "Сборка и швы": ["швы", "нитки", "расползается", "кривые швы", "обтрепался", "сборка", "развалился"],
            "Запах и химия": ["запах", "воняет", "химический запах", "пахнет", "вонь", "неприятный запах", "токсичный"],
            "Логистика": ["доставка", "упаковка", "помят", "поврежден", "курьер", "испорчен", "битый"],
            "Соответствие описанию": ["обман", "не соответствует", "другой товар", "подделка", "врут", "неправда", "не то"],
            "Общее разочарование": ["не советую", "ужас", "кошмар", "верните деньги", "жалею", "отвратительно", "разочарован"]
        }
        
        total_reviews = len(russian_reviews)
        problem_stats = {}
        critical_reviews = []
        positive_reviews = []
        neutral_reviews = []
        
        # Инициализируем проблемы
        for problem_name in enhanced_problems:
            problem_stats[problem_name] = {
                "count": 0,
                "percentage": 0,
                "examples": [],
                "detailed_reviews": []
            }
        
        for review in russian_reviews:
            text = review.get('review_text', '').lower()
            rating = review.get('rating', 5)
            original_text = review.get('review_text', '')
            
            review_data = {
                'text': original_text,
                'rating': rating,
                'date': review.get('date', ''),
                'short_text': original_text[:250] + "..." if len(original_text) > 250 else original_text
            }
            
            if rating <= 3:
                critical_reviews.append(review_data)
            elif rating >= 5:
                positive_reviews.append(review_data)
            else:
                neutral_reviews.append(review_data)
            
            # Поиск проблем с весами
            for problem_name, keywords in enhanced_problems.items():
                problem_found = False
                for keyword in keywords:
                    if keyword in text:
                        problem_stats[problem_name]["count"] += 1
                        if len(problem_stats[problem_name]["examples"]) < 2:
                            example = original_text[:200].strip()
                            if example:
                                problem_stats[problem_name]["examples"].append(example + "...")
                        if len(problem_stats[problem_name]["detailed_reviews"]) < 3:
                            problem_stats[problem_name]["detailed_reviews"].append(review_data)
                        problem_found = True
                        break
                if problem_found:
                    break  # Один отзыв = одна проблема
        
        # Вычисляем проценты
        for problem_name, data in problem_stats.items():
            if data["count"] > 0:
                data["percentage"] = round((data["count"] / total_reviews) * 100, 1)
        
        # Сортируем проблемы
        sorted_problems = sorted(
            [(name, data) for name, data in problem_stats.items() if data["count"] > 0],
            key=lambda x: x[1]["percentage"],
            reverse=True
        )
        
        best_positive = sorted(positive_reviews, key=lambda x: len(x['text']), reverse=True)[:3]
        worst_negative = sorted(critical_reviews, key=lambda x: len(x['text']), reverse=True)[:10]  # 10 критических
        
        # Базовый анализ готов
        basic_analysis = {
            "product_name": product_name,
            "category": category,
            "total_reviews": len(reviews),
            "russian_reviews": total_reviews,
            "critical_reviews_count": len(critical_reviews),
            "positive_reviews_count": len(positive_reviews),
            "neutral_reviews_count": len(neutral_reviews),
            "problems": sorted_problems,
            "best_positive_reviews": best_positive,
            "worst_negative_reviews": worst_negative,
            "all_reviews": russian_reviews
        }
        
        print("🤖 ЗАПУСК ESOLLL AI PROFESSIONAL ENGINE...")
        esolll_ai_analysis = await self.analyze_with_esolll_ai(russian_reviews, product_name, basic_analysis)
        
        # Объединяем анализы
        basic_analysis["esolll_ai_analysis"] = esolll_ai_analysis
        basic_analysis["ai_powered"] = True
        
        return basic_analysis
    
    def calculate_risk_with_esolll_ai(self, analysis):
        """Профессиональный расчет рисков с ESOLLL AI"""
        if not analysis:
            return {
                "decision": "НЕТ",
                "decision_emoji": "❌",
                "decision_reason": "Недостаточно данных для анализа",
                "risk_score": 100,
                "critical_percentage": 0,
                "positive_percentage": 0,
                "esolll_ai_influence": False
            }
        
        total_reviews = analysis["russian_reviews"]
        critical_percentage = (analysis["critical_reviews_count"] / total_reviews) * 100
        positive_percentage = (analysis["positive_reviews_count"] / total_reviews) * 100
        problems_count = len(analysis["problems"])
        top_problem_percentage = analysis["problems"][0][1]["percentage"] if analysis["problems"] else 0
        
        risk_score = 0
        
        # Базовые факторы риска
        if critical_percentage > 35:
            risk_score += 45
        elif critical_percentage > 20:
            risk_score += 25
        elif critical_percentage > 10:
            risk_score += 10
        
        if top_problem_percentage > 40:
            risk_score += 30
        elif top_problem_percentage > 25:
            risk_score += 20
        elif top_problem_percentage > 15:
            risk_score += 10
        
        if problems_count >= 6:
            risk_score += 20
        elif problems_count >= 4:
            risk_score += 15
        elif problems_count >= 2:
            risk_score += 10
        
        # Позитивные факторы
        if positive_percentage > 70:
            risk_score -= 15
        elif positive_percentage > 50:
            risk_score -= 10
        elif positive_percentage > 30:
            risk_score -= 5
        
        # ESOLLL AI влияние на оценку
        esolll_ai_influence = False
        if "esolll_ai_analysis" in analysis:
            esolll_ai = analysis["esolll_ai_analysis"]
            esolll_ai_influence = True
            
            # AI корректировки
            ai_rating = esolll_ai.get("esolll_score", {}).get("product_rating", "7")
            try:
                ai_rating_num = float(ai_rating)
            except:
                ai_rating_num = 7
            
            frustration = esolll_ai.get("emotional_profile", {}).get("frustration_level", "5")
            try:
                frustration_num = int(frustration)
            except:
                frustration_num = 5
            
            risk_level = esolll_ai.get("esolll_score", {}).get("risk_level", "средний")
            
            # AI корректировки риска
            if ai_rating_num <= 4:
                risk_score += 30
            elif ai_rating_num <= 6:
                risk_score += 15
            elif ai_rating_num >= 9:
                risk_score -= 20
            elif ai_rating_num >= 8:
                risk_score -= 10
            
            if frustration_num >= 8:
                risk_score += 25
            elif frustration_num >= 6:
                risk_score += 15
            elif frustration_num <= 3:
                risk_score -= 15
            
            if "критический" in risk_level.lower():
                risk_score += 25
            elif "высокий" in risk_level.lower():
                risk_score += 15
            elif "низкий" in risk_level.lower():
                risk_score -= 15
        
        risk_score = max(0, min(100, risk_score))
        
        # Финальное решение
        if risk_score >= 65:
            decision = "НЕТ"
            decision_emoji = "❌"
            reason = f"ВЫСОКИЙ РИСК: {critical_percentage:.1f}% критических отзывов"
            if esolll_ai_influence:
                reason += " + ESOLLL AI подтверждает риски"
        elif risk_score >= 35:
            decision = "ОСТОРОЖНО"
            decision_emoji = "⚠️"
            reason = f"СРЕДНИЙ РИСК: {critical_percentage:.1f}% критических отзывов"
            if esolll_ai_influence:
                reason += " + ESOLLL AI рекомендует осторожность"
        else:
            decision = "ПОКУПАТЬ"
            decision_emoji = "✅"
            reason = f"НИЗКИЙ РИСК: {critical_percentage:.1f}% критических отзывов"
            if esolll_ai_influence:
                reason += " + ESOLLL AI одобряет товар"
        
        return {
            "decision": decision,
            "decision_emoji": decision_emoji,
            "decision_reason": reason,
            "risk_score": risk_score,
            "critical_percentage": round(critical_percentage, 1),
            "positive_percentage": round(positive_percentage, 1),
            "esolll_ai_influence": esolll_ai_influence,
            "esolll_ai_rating": ai_rating if esolll_ai_influence else None
        }

class EsolllEnhancedParser:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'X-Mpstats-TOKEN': api_key,
            'Content-Type': 'application/json'
        }
    
    async def get_product_info(self, article_id):
        async with aiohttp.ClientSession() as session:
            try:
                url = f"https://mpstats.io/api/wb/get/item/{article_id}"
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=12)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'item' in data and data['item']:
                            product = data['item']
                            return {
                                'id': article_id,
                                'name': product.get('name', f'Товар WB {article_id}'),
                                'brand': product.get('brand', ''),
                                'rating': product.get('rating', 0),
                                'comments': product.get('comments', 0),
                                'price': product.get('final_price', product.get('price', 0)),
                                'found': True
                            }
                        else:
                            return None
                    else:
                        return None
            except Exception as e:
                print(f"❌ Ошибка получения товара: {e}")
                return None
    
    async def get_extended_reviews(self, article_id, target_reviews=120):
        url = f"https://mpstats.io/api/wb/get/item/{article_id}/comments"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=25)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, dict) and 'comments' in data:
                            comments = data['comments']
                            if comments and len(comments) > 0:
                                selected_comments = comments[:target_reviews]
                                normalized_reviews = []
                                for comment in selected_comments:
                                    if comment.get('text') and len(comment.get('text', '').strip()) >= 15:
                                        normalized_review = {
                                            'text': comment.get('text', ''),
                                            'review_text': comment.get('text', ''),
                                            'rating': comment.get('valuation', 5),
                                            'review_rating': comment.get('valuation', 5),
                                            'valuation': comment.get('valuation', 5),
                                            'date': comment.get('date', ''),
                                            'answer': comment.get('answer', '')
                                        }
                                        normalized_reviews.append(normalized_review)
                                return normalized_reviews
                            else:
                                return None
                        else:
                            return None
                    else:
                        return None
            except Exception as e:
                print(f"❌ Ошибка загрузки отзывов: {e}")
                return None

class EsolllAIReporter:
    def __init__(self):
        self.version = "ESOLLL AI Professional Analytics Engine"
    
    def select_top_10_critical_reviews(self, analysis):
        """🎯 ОТБОР 10 САМЫХ КРИТИЧЕСКИХ ОТЗЫВОВ"""
        if not analysis.get('all_reviews'):
            return []
        
        product_name = analysis.get('product_name', '')
        
        # Умные проблемы в зависимости от товара
        smart_problems = self.get_smart_problem_categories(product_name)
        
        # Собираем все ключевые слова
        all_keywords = []
        for keywords_list in smart_problems.values():
            all_keywords.extend(keywords_list)
        
        # Негативные индикаторы
        negative_indicators = ['плохо', 'ужасно', 'отвратительно', 'разочарован', 'жалею', 'верните', 
                              'не рекомендую', 'не советую', 'бред', 'фигня', 'отстой', 'развод',
                              'кошмар', 'ужас', 'деньги на ветер', 'обман', 'подделка']
        
        candidate_reviews = []
        
        # Анализируем каждый отзыв
        for review in analysis['all_reviews']:
            rating = review.get('rating', 5)
            text = review.get('text', '')
            text_lower = text.lower()
            
            # Исключаем хорошие отзывы и слишком короткие
            if rating >= 5 or len(text.strip()) < 30:
                continue
            
            review_score = 0
            matched_problems = []
            
            # Поиск проблем по категориям
            for problem_category, keywords in smart_problems.items():
                matches = sum(1 for keyword in keywords if keyword in text_lower)
                if matches > 0:
                    matched_problems.append({
                        'name': problem_category,
                        'severity': 'высокая' if matches >= 2 else 'средняя',
                        'matches': matches
                    })
                    review_score += matches * 6  # Высокий вес за совпадения
            
            # Поиск негативных индикаторов
            negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
            review_score += negative_count * 4
            
            # Бонусы за рейтинг
            if rating <= 2:
                review_score += 20
            elif rating == 3:
                review_score += 15
            elif rating == 4:
                review_score += 8
            
            # Бонус за длину (больше деталей)
            if len(text) > 100:
                review_score += 5
            if len(text) > 200:
                review_score += 5
            
            # Минимальный порог для попадания
            if review_score >= 8:
                if not matched_problems:
                    matched_problems = [{'name': 'Общее недовольство', 'severity': 'средняя', 'matches': 1}]
                
                candidate_reviews.append({
                    'text': text,
                    'rating': rating,
                    'date': review.get('date', ''),
                    'score': review_score,
                    'matched_problems': matched_problems,
                    'problem_summary': self.extract_problem_summary(text, matched_problems)
                })
        
        # Сортируем по критичности
        candidate_reviews.sort(key=lambda x: (x['score'], 5 - x['rating'], len(x['text'])), reverse=True)
        
        # Возвращаем топ-10
        return candidate_reviews[:10]
    
    def get_smart_problem_categories(self, product_name):
        """Умная категоризация проблем в зависимости от товара"""
        product_lower = product_name.lower()
        
        if any(word in product_lower for word in ["сушилка", "центрифуга", "салат"]):
            return {
                "Проблемы сушки": ["не сушит", "плохо сушит", "мокрый", "влажный", "не высыхает"],
                "Механизм вращения": ["не крутится", "слабо крутится", "заедает", "тормозит", "медленно"],
                "Размер корзины": ["маленькая", "большая", "не помещается", "мало места"],
                "Качество сборки": ["разваливается", "хлипкий", "неустойчивый", "шатается"],
                "Материалы": ["пластик", "тонкий", "хрупкий", "некачественный материал"]
            }
        elif any(word in product_lower for word in ["наушники", "bluetooth", "tws"]):
            return {
                "Качество звука": ["тихий", "искажения", "басы", "звук плохой", "шипит"],
                "Bluetooth связь": ["не подключается", "отключается", "теряет связь", "bluetooth"],
                "Время работы": ["быстро разряжается", "не заряжается", "держит заряд", "батарея"],
                "Комфорт": ["выпадают", "неудобные", "давят", "болят уши"],
                "Микрофон": ["не слышно", "микрофон", "плохо слышат", "эхо"]
            }
        elif any(word in product_lower for word in ["зарядка", "кабель", "провод"]):
            return {
                "Скорость зарядки": ["медленно заряжает", "долго заряжается", "слабая зарядка"],
                "Надежность": ["ломается", "отходит", "не заряжает", "перестал работать"],
                "Размеры": ["короткий", "длинный", "не хватает длины"],
                "Совместимость": ["не подходит", "не совместим", "не работает с"],
                "Качество": ["тонкий", "дешевый", "рвется", "гнется"]
            }
        else:
            return {
                "Функциональность": ["не работает", "бракованный", "глючит", "сломался"],
                "Качество": ["дешевый", "хрупкий", "некачественный", "плохой"],
                "Размеры": ["размер", "маленький", "большой", "не подходит"],
                "Сборка": ["разваливается", "неустойчивый", "хлипкий", "плохая сборка"],
                "Материалы": ["материал", "пластик", "металл", "ткань"]
            }
    
    def extract_problem_summary(self, text, matched_problems):
        """Извлекает краткое описание проблемы"""
        sentences = text.split('.')
        problem_sentences = []
        
        for sentence in sentences[:3]:  # Первые 3 предложения
            sentence_clean = sentence.strip()
            if len(sentence_clean) > 15:
                for problem in matched_problems:
                    if any(word in sentence_clean.lower() for word in problem['name'].lower().split()):
                        problem_sentences.append(sentence_clean)
                        break
        
        if problem_sentences:
            return problem_sentences[0][:150] + "..." if len(problem_sentences[0]) > 150 else problem_sentences[0]
        else:
            return text[:120] + "..." if len(text) > 120 else text
    
    def create_critical_reviews_section(self, analysis):
        """📝 СЕКЦИЯ 10 КРИТИЧЕСКИХ ОТЗЫВОВ"""
        critical_reviews = self.select_top_10_critical_reviews(analysis)
        
        if not critical_reviews:
            return f"""
            <div class="critical-reviews-section">
                <h2>💬 Анализ критических отзывов</h2>
                <div class="excellent-status">
                    <div class="status-icon">🎉</div>
                    <h3>Отличный результат!</h3>
                    <p>Среди {analysis.get('total_reviews', 0)} отзывов серьезных критических замечаний не обнаружено.</p>
                    <div class="positive-indicators">
                        <div class="indicator">✅ Низкий уровень жалоб</div>
                        <div class="indicator">🏆 Высокое качество товара</div>
                        <div class="indicator">😊 Довольные покупатели</div>
                    </div>
                </div>
            </div>
            """
        
        reviews_html = f"""
        <div class="critical-reviews-section">
            <h2>💬 10 самых критических отзывов покупателей</h2>
            <div class="section-description">
                Детальный анализ основных проблем товара на основе реальных отзывов покупателей
            </div>
            
            <div class="reviews-stats">
                <div class="stat-card">
                    <div class="stat-number">{len(critical_reviews)}</div>
                    <div class="stat-label">Критических отзывов</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{analysis.get('total_reviews', 0)}</div>
                    <div class="stat-label">Всего отзывов</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{analysis.get('critical_percentage', 0)}%</div>
                    <div class="stat-label">Доля критических</div>
                </div>
            </div>
            
            <div class="critical-reviews-grid">"""
        
        for i, review in enumerate(critical_reviews, 1):
            severity_class = "severity-high" if review.get('score', 0) >= 20 else "severity-medium" if review.get('score', 0) >= 15 else "severity-low"
            severity_text = "КРИТИЧНО" if review.get('score', 0) >= 20 else "ВАЖНО" if review.get('score', 0) >= 15 else "ВНИМАНИЕ"
            
            problems_list = ", ".join([p.get('name', 'Проблема') for p in review.get('matched_problems', [])[:2]])
            if not problems_list:
                problems_list = "Общие недостатки"
            
            reviews_html += f"""
                <div class="critical-review-card {severity_class}">
                    <div class="review-header">
                        <div class="review-number">#{i}</div>
                        <div class="review-rating">⭐ {review.get('rating', 1)}/5</div>
                        <div class="severity-badge">{severity_text}</div>
                    </div>
                    
                    <div class="review-content">
                        <div class="review-text">
                            "{review.get('text', 'Текст недоступен')}"
                        </div>
                        
                        <div class="review-analysis">
                            <div class="problems-found">
                                <strong>🎯 Выявленные проблемы:</strong> {problems_list}
                            </div>
                            <div class="problem-summary">
                                <strong>📋 Суть проблемы:</strong> {review.get('problem_summary', 'Анализируется')}
                            </div>
                        </div>
                        
                        <div class="review-meta">
                            <span class="review-date">📅 {review.get('date', 'Дата не указана')}</span>
                            <span class="review-score">Критичность: {review.get('score', 0)}/30</span>
                        </div>
                    </div>
                </div>"""
        
        reviews_html += """
            </div>
        </div>"""
        
        return reviews_html
    
    def create_esolll_ai_insights_section(self, esolll_ai_analysis):
        """🤖 СЕКЦИЯ ESOLLL AI INSIGHTS"""
        if not esolll_ai_analysis:
            return """
            <div class="ai-unavailable">
                <h3>🤖 ESOLLL AI Professional Engine временно недоступен</h3>
                <p>Используется базовый алгоритм анализа</p>
            </div>
            """
        
        ai_problems = esolll_ai_analysis.get("esolll_ai_problems", [])
        emotional_profile = esolll_ai_analysis.get("emotional_profile", {})
        insights = esolll_ai_analysis.get("professional_insights", {})
        predictions = esolll_ai_analysis.get("esolll_predictions", {})
        esolll_score = esolll_ai_analysis.get("esolll_score", {})
        
        ai_html = f"""
        <div class="esolll-ai-section">
            <div class="ai-header">
                <div class="ai-logo">🤖</div>
                <div class="ai-title">
                    <h2>ESOLLL AI Professional Analytics Engine</h2>
                    <p>Профессиональный анализ с искусственным интеллектом</p>
                </div>
                <div class="ai-badge">AI PRO</div>
            </div>
            
            <div class="ai-score-panel">
                <div class="main-score">
                    <div class="score-value">{esolll_score.get('product_rating', 'N/A')}/10</div>
                    <div class="score-title">ESOLLL AI Оценка</div>
                </div>
                <div class="recommendation-panel">
                    <div class="recommendation {self.get_recommendation_class(esolll_score.get('buy_recommendation', 'осторожно'))}">
                        {esolll_score.get('buy_recommendation', 'осторожно').upper()}
                    </div>
                    <div class="risk-level">Риск: {esolll_score.get('risk_level', 'средний')}</div>
                    <div class="confidence">Уверенность: {esolll_score.get('confidence', 'средняя')}</div>
                </div>
            </div>
            
            <div class="ai-insights-grid">
                <div class="ai-card problems-card">
                    <h3>🧠 AI-обнаруженные проблемы</h3>
                    <div class="ai-problems-list">"""
        
        for problem in ai_problems[:4]:
            severity = problem.get('severity', 'средняя')
            severity_class = self.get_severity_class(severity)
            ai_html += f"""
                        <div class="ai-problem {severity_class}">
                            <div class="problem-name">{problem.get('name', 'Проблема')}</div>
                            <div class="problem-description">{problem.get('description', 'Описание недоступно')}</div>
                            <div class="problem-meta">
                                <span class="severity">Серьезность: {severity}</span>
                                <span class="frequency">Частота: {problem.get('frequency_estimate', 'неизвестно')}</span>
                            </div>
                        </div>"""
        
        ai_html += f"""
                    </div>
                </div>
                
                <div class="ai-card emotional-card">
                    <h3>💭 Эмоциональный профиль</h3>
                    <div class="emotional-metrics">
                        <div class="metric">
                            <span class="metric-label">Общее настроение:</span>
                            <span class="metric-value {self.get_mood_class(emotional_profile.get('overall_mood', 'нейтральный'))}">{emotional_profile.get('overall_mood', 'нейтральный')}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Уровень фрустрации:</span>
                            <span class="metric-value frustration-level">{emotional_profile.get('frustration_level', '5')}/10</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Риск потери лояльности:</span>
                            <span class="metric-value">{emotional_profile.get('loyalty_risk', 'неопределен')}</span>
                        </div>
                    </div>
                    
                    <div class="emotional-details">
                        <div class="satisfaction-triggers">
                            <h4>😊 Что радует:</h4>
                            <ul>"""
        
        for trigger in emotional_profile.get('satisfaction_triggers', ['Анализируется...'])[:3]:
            ai_html += f"<li>{trigger}</li>"
        
        ai_html += f"""
                            </ul>
                        </div>
                        <div class="pain-triggers">
                            <h4>😰 Что расстраивает:</h4>
                            <ul>"""
        
        for trigger in emotional_profile.get('pain_triggers', ['Анализируется...'])[:3]:
            ai_html += f"<li>{trigger}</li>"
        
        ai_html += f"""
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="ai-recommendations-row">
                <div class="ai-card recommendations-card">
                    <h3>🎯 Профессиональные рекомендации ESOLLL AI</h3>
                    
                    <div class="recommendations-section">
                        <div class="immediate-fixes">
                            <h4>🚨 Срочные исправления:</h4>
                            <ul>"""
        
        for fix in insights.get('immediate_fixes', ['AI анализ в процессе'])[:4]:
            ai_html += f"<li>{fix}</li>"
        
        ai_html += f"""
                            </ul>
                        </div>
                        
                        <div class="strategic-improvements">
                            <h4>📈 Стратегические улучшения:</h4>
                            <ul>"""
        
        for improvement in insights.get('strategic_improvements', ['AI анализ в процессе'])[:4]:
            ai_html += f"<li>{improvement}</li>"
        
        ai_html += f"""
                            </ul>
                        </div>
                    </div>
                    
                    <div class="business-insights">
                        <div class="insight-item">
                            <strong>Конкурентная позиция:</strong> {insights.get('competitive_positioning', 'Анализируется')}
                        </div>
                        <div class="insight-item">
                            <strong>Рыночные возможности:</strong> {', '.join(insights.get('market_opportunities', ['Определяются'])[:2])}
                        </div>
                        <div class="insight-item">
                            <strong>Критические риски:</strong> {', '.join(insights.get('critical_risks', ['Анализируются'])[:2])}
                        </div>
                    </div>
                </div>
                
                <div class="ai-card predictions-card">
                    <h3>🔮 AI-прогнозы ESOLLL</h3>
                    <div class="predictions-grid">
                        <div class="prediction-item">
                            <div class="prediction-label">Тренд продаж:</div>
                            <div class="prediction-value">{predictions.get('sales_trend', 'Анализируется')}</div>
                        </div>
                        <div class="prediction-item">
                            <div class="prediction-label">Качество товара:</div>
                            <div class="prediction-value">{predictions.get('quality_trend', 'Анализируется')}</div>
                        </div>
                        <div class="prediction-item">
                            <div class="prediction-label">Удержание клиентов:</div>
                            <div class="prediction-value">{predictions.get('customer_retention', 'Прогнозируется')}</div>
                        </div>
                        <div class="prediction-item">
                            <div class="prediction-label">Прогноз возвратов:</div>
                            <div class="prediction-value">{predictions.get('return_forecast', 'Рассчитывается')}</div>
                        </div>
                        <div class="prediction-item">
                            <div class="prediction-label">Сроки улучшений:</div>
                            <div class="prediction-value">{predictions.get('improvement_timeline', 'Планируются')}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>"""
        
        return ai_html
    
    def get_recommendation_class(self, recommendation):
        if recommendation.lower() in ['покупать']:
            return 'rec-positive'
        elif recommendation.lower() in ['не_покупать']:
            return 'rec-negative'
        else:
            return 'rec-neutral'
    
    def get_severity_class(self, severity):
        if severity.lower() in ['критическая', 'высокая']:
            return 'sev-high'
        elif severity.lower() == 'средняя':
            return 'sev-medium'
        else:
            return 'sev-low'
    
    def get_mood_class(self, mood):
        if mood.lower() == 'позитивный':
            return 'mood-positive'
        elif mood.lower() == 'негативный':
            return 'mood-negative'
        else:
            return 'mood-neutral'
    
    def generate_esolll_ai_report(self, analysis, risk_data, article_id, product_data):
        """🚀 ГЕНЕРАЦИЯ ФИНАЛЬНОГО ESOLLL AI ОТЧЕТА"""
        try:
            esolll_ai_analysis = analysis.get("esolll_ai_analysis", {})
            critical_reviews_section = self.create_critical_reviews_section(analysis)
            ai_insights_section = self.create_esolll_ai_insights_section(esolll_ai_analysis)
            
            html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESOLLL AI Professional Report - {article_id}</title>
    <style>
        {self.get_esolll_professional_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self.create_professional_header(article_id)}
        
        <div class="product-section">
            <div class="product-card">
                <div class="product-name">📦 {product_data['name']}</div>
                <div class="product-details">
                    <div class="detail-item">
                        <div class="detail-value">{product_data['brand']}</div>
                        <div class="detail-label">Бренд</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-value">⭐ {product_data['rating']}/5</div>
                        <div class="detail-label">Рейтинг</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-value">{product_data['comments']}</div>
                        <div class="detail-label">Отзывов</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-value">{product_data['price']} ₽</div>
                        <div class="detail-label">Цена</div>
                    </div>
                </div>
            </div>
        </div>
        
        {self.create_professional_decision_box(risk_data)}
        
        {critical_reviews_section}
        
        {ai_insights_section}
        
        <div class="pdf-export-section">
            <div class="export-header">
                <h3>📄 Экспорт профессионального отчета</h3>
                <p>Сохраните полный анализ ESOLLL AI в формате PDF</p>
            </div>
            
            <div class="export-buttons">
                <button onclick="window.print()" class="export-btn primary">
                    🖨️ Скачать PDF
                </button>
                <button onclick="shareReport()" class="export-btn secondary">
                    📤 Поделиться
                </button>
            </div>
            
            <div class="export-features">
                <div class="feature-item">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-text">
                        <strong>ESOLLL AI анализ</strong><br>
                        Профессиональные инсайты сохранятся
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">💬</div>
                    <div class="feature-text">
                        <strong>10 критических отзывов</strong><br>
                        Полные тексты в отчете
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">📱</div>
                    <div class="feature-text">
                        <strong>Мобильная оптимизация</strong><br>
                        Читается на всех устройствах
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        function shareReport() {{
            if (navigator.share) {{
                navigator.share({{
                    title: 'ESOLLL AI Professional Report',
                    text: 'Профессиональный анализ товара от ESOLLL AI',
                    url: window.location.href
                }});
            }} else {{
                navigator.clipboard.writeText(window.location.href).then(() => {{
                    alert('🔗 Ссылка скопирована в буфер обмена!');
                }});
            }}
        }}
        
        window.addEventListener('beforeprint', function() {{
            document.body.classList.add('printing');
        }});
        
        window.addEventListener('afterprint', function() {{
            document.body.classList.remove('printing');
        }});
        </script>
        
        {self.create_professional_footer()}
    </div>
</body>
</html>
            """
            
            return html_content
            
        except Exception as e:
            print(f"❌ ОШИБКА ГЕНЕРАЦИИ ESOLLL AI ОТЧЕТА: {e}")
            return self.generate_error_report(article_id)
    
    def create_professional_header(self, article_id):
        return f"""
        <div class="professional-header">
            <div class="header-badge">AI PROFESSIONAL</div>
            <div class="ai-icon">🤖</div>
            <h1>ESOLLL AI Professional Analytics Engine</h1>
            <p>Революционный анализ товаров с искусственным интеллектом • Артикул: {article_id}</p>
            <div class="capabilities">
                <span class="capability">🧠 Семантический анализ</span>
                <span class="capability">💭 Эмоциональная аналитика</span>
                <span class="capability">🔮 AI-прогнозы</span>
                <span class="capability">🎯 Профессиональные рекомендации</span>
            </div>
            <p class="developer">Разработчик: Almas Kasymzhanov</p>
        </div>
        """
    
    def create_professional_decision_box(self, risk_data):
        decision_class = 'decision-neutral'
        if risk_data['decision'] == 'ПОКУПАТЬ':
            decision_class = 'decision-positive'
        elif risk_data['decision'] == 'НЕТ':
            decision_class = 'decision-negative'
        
        esolll_ai_text = ""
        if risk_data.get('esolll_ai_influence'):
            esolll_ai_text = f"<br><div class='ai-influence'>🤖 ESOLLL AI оценка: {risk_data.get('esolll_ai_rating', 'неопределено')}/10</div>"
        
        return f"""
        <div class="professional-decision {decision_class}">
            {risk_data['decision_emoji']} <strong>ESOLLL AI РЕШЕНИЕ: {risk_data['decision']}</strong>
            <div class="decision-details">
                {risk_data['decision_reason']}
                {esolll_ai_text}
            </div>
        </div>
        """
    
    def get_esolll_professional_styles(self):
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 24px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        /* ПРОФЕССИОНАЛЬНЫЙ ЗАГОЛОВОК */
        .professional-header {
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            color: white;
            padding: 50px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .professional-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 50%);
            animation: pulse 6s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.3; }
            50% { transform: scale(1.2) rotate(180deg); opacity: 0.7; }
        }
        
        .header-badge {
            position: absolute;
            top: 25px;
            right: 25px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            padding: 12px 20px;
            border-radius: 30px;
            font-weight: bold;
            font-size: 14px;
            box-shadow: 0 8px 25px rgba(255,107,107,0.4);
            z-index: 10;
        }
        
        .ai-icon {
            font-size: 64px;
            margin-bottom: 20px;
            animation: float 4s ease-in-out infinite;
            z-index: 5;
            position: relative;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
        }
        
        .professional-header h1 {
            font-size: 38px;
            font-weight: 700;
            margin-bottom: 15px;
            z-index: 5;
            position: relative;
        }
        
        .professional-header > p {
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 25px;
            z-index: 5;
            position: relative;
        }
        
        .capabilities {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 20px;
            z-index: 5;
            position: relative;
        }
        
        .capability {
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            backdrop-filter: blur(10px);
        }
        
        .developer {
            font-size: 14px;
            opacity: 0.8;
            z-index: 5;
            position: relative;
        }
        
        /* ПРОДУКТ СЕКЦИЯ */
        .product-section {
            padding: 40px;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        }
        
        .product-card {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.1);
            border-left: 6px solid #667eea;
        }
        
        .product-name {
            font-size: 24px;
            font-weight: 700;
            color: #333;
            margin-bottom: 25px;
        }
        
        .product-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .detail-item {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #f8f9fa, #ffffff);
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        
        .detail-value {
            font-size: 22px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .detail-label {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }
        
        /* РЕШЕНИЕ */
        .professional-decision {
            margin: 40px;
            padding: 35px;
            border-radius: 20px;
            text-align: center;
            font-size: 22px;
            font-weight: 700;
            box-shadow: 0 15px 50px rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
        }
        
        .professional-decision::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shine 4s infinite;
        }
        
        @keyframes shine {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .decision-details {
            font-size: 16px;
            font-weight: 400;
            margin-top: 15px;
            z-index: 2;
            position: relative;
        }
        
        .ai-influence {
            background: rgba(255,255,255,0.3);
            padding: 10px 20px;
            border-radius: 15px;
            display: inline-block;
            margin-top: 15px;
            font-size: 14px;
            backdrop-filter: blur(10px);
        }
        
        .decision-positive {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724;
            border: 3px solid #28a745;
        }
        
        .decision-negative {
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            color: #721c24;
            border: 3px solid #dc3545;
        }
        
        .decision-neutral {
            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
            color: #856404;
            border: 3px solid #ffc107;
        }
        
        /* КРИТИЧЕСКИЕ ОТЗЫВЫ */
        .critical-reviews-section {
            padding: 40px;
            background: linear-gradient(135deg, #fff5f5, #ffeee8);
        }
        
        .critical-reviews-section h2 {
            color: #dc3545;
            font-size: 28px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 700;
        }
        
        .section-description {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 16px;
            font-style: italic;
        }
        
        .reviews-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(220,53,69,0.1);
            border-top: 4px solid #dc3545;
        }
        
        .stat-number {
            font-size: 32px;
            font-weight: 700;
            color: #dc3545;
            margin-bottom: 8px;
        }
        
        .stat-label {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }
        
        .critical-reviews-grid {
            display: grid;
            gap: 25px;
        }
        
        .critical-review-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            border-left: 6px solid #dc3545;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .critical-review-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 60px rgba(0,0,0,0.15);
        }
        
        .severity-high { border-left-color: #dc3545; }
        .severity-medium { border-left-color: #fd7e14; }
        .severity-low { border-left-color: #ffc107; }
        
        .review-header {
            background: linear-gradient(135deg, #fff5f5, #ffeee8);
            padding: 20px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .review-number {
            background: #dc3545;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
        }
        
        .review-rating {
            font-weight: 700;
            color: #dc3545;
            font-size: 16px;
        }
        
        .severity-badge {
            background: #dc3545;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
        }
        
        .review-content {
            padding: 25px;
        }
        
        .review-text {
            font-size: 16px;
            line-height: 1.7;
            color: #333;
            font-style: italic;
            margin-bottom: 20px;
            padding: 20px;
            background: #fff5f5;
            border-radius: 12px;
            border-left: 4px solid #dc3545;
        }
        
        .review-analysis {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
        }
        
        .problems-found, .problem-summary {
            margin-bottom: 10px;
            font-size: 14px;
            color: #495057;
        }
        
        .review-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: #666;
            padding-top: 15px;
            border-top: 1px solid #f0f0f0;
        }
        
        .excellent-status {
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #f0f8ff, #e8f5e8);
            border-radius: 20px;
            margin: 30px 0;
            border: 3px solid #28a745;
        }
        
        .status-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        
        .excellent-status h3 {
            color: #28a745;
            font-size: 28px;
            margin-bottom: 20px;
        }
        
        .excellent-status p {
            color: #666;
            font-size: 18px;
            margin-bottom: 25px;
        }
        
        .positive-indicators {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .indicator {
            background: white;
            padding: 15px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 500;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        /* ESOLLL AI СЕКЦИЯ */
        .esolll-ai-section {
            padding: 40px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .esolll-ai-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="15" height="15" patternUnits="userSpaceOnUse"><path d="M 15 0 L 0 0 0 15" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.4;
        }
        
        .ai-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 40px;
            position: relative;
            z-index: 5;
        }
        
        .ai-logo {
            font-size: 72px;
            animation: float 4s ease-in-out infinite;
        }
        
        .ai-title h2 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .ai-title p {
            opacity: 0.9;
            font-size: 16px;
        }
        
        .ai-badge {
            background: rgba(255,255,255,0.2);
            padding: 15px 25px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 16px;
            backdrop-filter: blur(15px);
        }
        
        .ai-score-panel {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.15);
            padding: 30px;
            border-radius: 25px;
            margin-bottom: 40px;
            backdrop-filter: blur(15px);
            position: relative;
            z-index: 5;
        }
        
        .main-score {
            text-align: center;
        }
        
        .score-value {
            font-size: 64px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 10px;
        }
        
        .score-title {
            font-size: 16px;
            opacity: 0.9;
            font-weight: 500;
        }
        
        .recommendation-panel {
            text-align: center;
        }
        
        .recommendation {
            padding: 15px 30px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 20px;
            margin-bottom: 12px;
            display: inline-block;
        }
        
        .rec-positive { background: #28a745; color: white; }
        .rec-negative { background: #dc3545; color: white; }
        .rec-neutral { background: #ffc107; color: #856404; }
        
        .risk-level, .confidence {
            font-size: 14px;
            opacity: 0.8;
            margin: 5px 0;
        }
        
        .ai-insights-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
            position: relative;
            z-index: 5;
        }
        
        .ai-card {
            background: rgba(255,255,255,0.95);
            color: #333;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
            backdrop-filter: blur(15px);
        }
        
        .ai-card h3 {
            color: #667eea;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 25px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .ai-problems-list {
            display: grid;
            gap: 20px;
        }
        
        .ai-problem {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }
        
        .sev-high { border-left-color: #dc3545; }
        .sev-medium { border-left-color: #fd7e14; }
        .sev-low { border-left-color: #28a745; }
        
        .problem-name {
            font-weight: 700;
            color: #333;
            font-size: 16px;
            margin-bottom: 8px;
        }
        
        .problem-description {
            color: #666;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        
        .problem-meta {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #999;
        }
        
        .emotional-metrics {
            margin-bottom: 25px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .metric-label {
            font-weight: 600;
        }
        
        .metric-value {
            font-weight: 700;
        }
        
        .mood-positive { color: #28a745; }
        .mood-negative { color: #dc3545; }
        .mood-neutral { color: #ffc107; }
        
        .frustration-level {
            color: #fd7e14;
        }
        
        .emotional-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .satisfaction-triggers h4, .pain-triggers h4 {
            color: #667eea;
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        .satisfaction-triggers ul, .pain-triggers ul {
            padding-left: 20px;
        }
        
        .satisfaction-triggers li, .pain-triggers li {
            font-size: 13px;
            margin: 8px 0;
            line-height: 1.4;
        }
        
        .ai-recommendations-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            position: relative;
            z-index: 5;
        }
        
        .recommendations-section {
            margin-bottom: 25px;
        }
        
        .immediate-fixes h4, .strategic-improvements h4 {
            color: #667eea;
            font-size: 16px;
            margin-bottom: 15px;
        }
        
        .immediate-fixes ul, .strategic-improvements ul {
            padding-left: 20px;
            margin-bottom: 20px;
        }
        
        .immediate-fixes li, .strategic-improvements li {
            font-size: 14px;
            margin: 10px 0;
            line-height: 1.5;
        }
        
        .business-insights {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
        }
        
        .insight-item {
            margin: 12px 0;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .predictions-grid {
            display: grid;
            gap: 15px;
        }
        
        .prediction-item {
            display: flex;
            justify-content: space-between;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
            font-size: 14px;
        }
        
        .prediction-label {
            font-weight: 600;
        }
        
        .prediction-value {
            font-weight: 700;
            color: #667eea;
        }
        
        .ai-unavailable {
            padding: 40px;
            text-align: center;
            background: #fff3cd;
            border: 3px solid #ffc107;
            border-radius: 20px;
            margin: 40px;
        }
        
        .ai-unavailable h3 {
            color: #856404;
            margin-bottom: 15px;
            font-size: 24px;
        }
        
        .ai-unavailable p {
            color: #856404;
            font-size: 16px;
        }
        
        /* PDF ЭКСПОРТ */
        .pdf-export-section {
            padding: 40px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-align: center;
        }
        
        .export-header h3 {
            font-size: 32px;
            margin-bottom: 15px;
            font-weight: 700;
        }
        
        .export-header p {
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 30px;
        }
        
        .export-buttons {
            display: flex;
            justify-content: center;
            gap: 25px;
            margin: 35px 0;
        }
        
        .export-btn {
            padding: 18px 35px;
            border: none;
            border-radius: 15px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 200px;
        }
        
        .export-btn.primary {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            box-shadow: 0 10px 30px rgba(40,167,69,0.4);
        }
        
        .export-btn.secondary {
            background: linear-gradient(135deg, #fd7e14, #e83e8c);
            color: white;
            box-shadow: 0 10px 30px rgba(253,126,20,0.4);
        }
        
        .export-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .export-features {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
            margin-top: 40px;
        }
        
        .feature-item {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(15px);
        }
        
        .feature-icon {
            font-size: 40px;
            margin-bottom: 15px;
        }
        
        .feature-text strong {
            display: block;
            font-size: 18px;
            margin-bottom: 8px;
        }
        
        .feature-text {
            font-size: 14px;
            line-height: 1.5;
        }
        
        /* ФУТЕР */
        .professional-footer {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            margin-bottom: 25px;
        }
        
        .footer-section {
            font-size: 14px;
            line-height: 1.6;
        }
        
        .footer-note {
            font-size: 12px;
            opacity: 0.8;
            font-style: italic;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        
        /* АДАПТИВНОСТЬ */
        @media (max-width: 768px) {
            .container { margin: 10px; }
            .professional-header { padding: 30px 20px; }
            .professional-header h1 { font-size: 28px; }
            .ai-insights-grid { grid-template-columns: 1fr; }
            .ai-recommendations-row { grid-template-columns: 1fr; }
            .export-buttons { flex-direction: column; align-items: center; }
            .export-features { grid-template-columns: 1fr; }
            .footer-content { grid-template-columns: 1fr; }
            .capabilities { justify-content: center; }
            .ai-header { flex-direction: column; gap: 20px; text-align: center; }
            .ai-score-panel { flex-direction: column; gap: 25px; }
            .emotional-details { grid-template-columns: 1fr; }
        }
        
        /* ПЕЧАТЬ */
        @media print {
            .pdf-export-section { display: none; }
            * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }
            body { background: white !important; }
            .container { box-shadow: none !important; }
            .professional-header { -webkit-print-color-adjust: exact; }
            .esolll-ai-section { -webkit-print-color-adjust: exact; }
            .critical-review-card { page-break-inside: avoid; }
            .ai-card { page-break-inside: avoid; }
        }
        """
    
    def create_professional_footer(self):
        return f"""
        <div class="professional-footer">
            <div class="footer-content">
                <div class="footer-section">
                    <strong>🤖 ESOLLL AI Professional Analytics Engine</strong><br>
                    Революционная система анализа товаров с искусственным интеллектом
                </div>
                <div class="footer-section">
                    <strong>🆕 Professional возможности:</strong><br>
                    Семантический анализ • Эмоциональная аналитика • AI-прогнозы • 10 критических отзывов
                </div>
                <div class="footer-section">
                    <strong>👨‍💻 Разработчик: Almas Kasymzhanov</strong><br>
                    📅 ESOLLL AI Professional от {datetime.now().strftime('%d.%m.%Y')}
                </div>
            </div>
            <div class="footer-note">
                🧠 Анализ выполнен с использованием передовых алгоритмов машинного обучения и семантического анализа
            </div>
        </div>
        """
    
    def generate_error_report(self, article_id):
        return f"""
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>ESOLLL AI Professional Error</title></head>
<body style="text-align: center; padding: 50px; font-family: Arial;">
<h1>🤖 ESOLLL AI Professional Analytics Engine</h1>
<h2>⚠️ Недостаточно данных</h2>
<p>Товар {article_id} - недостаточно данных для профессионального анализа</p>
</body></html>
        """

class EsolllAIProfessionalBot:
    def __init__(self, telegram_token, mpstats_api_key, anthropic_api_key):
        self.telegram_token = telegram_token
        self.parser = EsolllEnhancedParser(mpstats_api_key)
        self.analyzer = EsolllAIAnalyzer(anthropic_api_key)
        self.reporter = EsolllAIReporter()
        self.offset = 0
        self.running = False
    
    async def send_message(self, chat_id, text, parse_mode='Markdown'):
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
            try:
                async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=12)) as response:
                    return response.status == 200
            except:
                return False
    
    async def send_document(self, chat_id, file_path, caption=""):
        if not os.path.exists(file_path):
            return False
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendDocument"
            try:
                with open(file_path, 'rb') as file:
                    data = aiohttp.FormData()
                    data.add_field('chat_id', str(chat_id))
                    data.add_field('document', file, filename=os.path.basename(file_path))
                    if caption:
                        data.add_field('caption', caption)
                    async with session.post(url, data=data, timeout=aiohttp.ClientTimeout(total=35)) as response:
                        return response.status == 200
            except Exception as e:
                print(f"❌ Ошибка отправки документа: {e}")
                return False
    
    async def analyze_product_professional(self, article_id, chat_id):
        start_msg = f"""🤖 **ESOLLL AI Professional Analytics Engine**
*Революционный анализ товаров с искусственным интеллектом*

🔍 Анализирую товар **{article_id}** с помощью ESOLLL AI
🚀 **PROFESSIONAL ВОЗМОЖНОСТИ:**
• 🧠 Семантический анализ отзывов
• 💭 Эмоциональная аналитика покупателей
• 🔮 AI-прогнозы и профессиональные рекомендации
• 📝 10 самых критических отзывов с анализом

⏳ *Получаю данные товара...*"""
        
        await self.send_message(chat_id, start_msg)
        
        try:
            product_data = await self.parser.get_product_info(article_id)
            
            if not product_data:
                error_msg = f"""❌ **Товар не найден**

Товар **{article_id}** не найден в базе MPStats.

🔄 **Попробуйте другой артикул**"""
                await self.send_message(chat_id, error_msg)
                return False
            
            found_msg = f"""✅ **Товар найден!**
📦 {product_data['name'][:60]}...
🏷️ Бренд: {product_data['brand']}
⭐ Рейтинг: {product_data['rating']}/5
💬 Всего отзывов: {product_data['comments']}

🤖 **Загружаю отзывы для ESOLLL AI анализа...**
🧠 **Подготавливаю профессиональную аналитику...**"""
            
            await self.send_message(chat_id, found_msg)
            
            reviews = await self.parser.get_extended_reviews(article_id, target_reviews=120)
            
            if not reviews:
                no_reviews_msg = f"""⚠️ **Отзывы недоступны**

Не удалось загрузить отзывы для ESOLLL AI анализа.
Проверьте настройки тарифа в MPStats."""
                await self.send_message(chat_id, no_reviews_msg)
                return False
            
            processing_msg = f"""✅ **Отзывы загружены успешно**
🤖 **ЗАПУСКАЮ ESOLLL AI PROFESSIONAL ENGINE...**
🧠 **Семантическая обработка {len(reviews)} отзывов...**
💭 **Анализ эмоций и настроений покупателей...**
📝 **Поиск 10 самых критических отзывов...**

⚡ *Это займет 30-90 секунд...*"""
            
            await self.send_message(chat_id, processing_msg)
            
            # ГЛАВНОЕ: запускаем ESOLLL AI Professional анализ
            analysis = await self.analyzer.analyze_with_esolll_professional(reviews, product_data['name'])
            
            if not analysis:
                no_data_msg = f"""⚠️ **Недостаточно данных для ESOLLL AI анализа**

Нужно больше качественных отзывов для профессионального анализа."""
                await self.send_message(chat_id, no_data_msg)
                return False
            
            # Показываем статус ESOLLL AI
            ai_status_msg = "🤖 **ESOLLL AI PROFESSIONAL АНАЛИЗ ЗАВЕРШЕН!**"
            if analysis.get("ai_powered"):
                esolll_ai_analysis = analysis.get("esolll_ai_analysis", {})
                ai_rating = esolll_ai_analysis.get("esolll_score", {}).get("product_rating", "неопределено")
                ai_status_msg += f"\n✅ **ESOLLL AI оценка товара: {ai_rating}/10**"
                ai_status_msg += "\n🧠 **Семантический анализ выполнен**"
                ai_status_msg += "\n💭 **Эмоциональная аналитика готова**"
                ai_status_msg += f"\n📝 **Найдено критических отзывов для анализа**"
            else:
                ai_status_msg += "\n⚠️ **Использован базовый алгоритм (ESOLLL AI временно недоступен)**"
            
            await self.send_message(chat_id, ai_status_msg)
            
            risk_data = self.analyzer.calculate_risk_with_esolll_ai(analysis)
            
            await self.send_message(chat_id, "🎯 **Создаю профессиональный ESOLLL AI отчет...**")
            
            await self.send_professional_results(chat_id, product_data, analysis, risk_data)
            await self.create_professional_report(chat_id, analysis, risk_data, article_id, product_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка ESOLLL AI Professional анализа: {e}")
            error_msg = f"""❌ **Ошибка ESOLLL AI Professional анализа**

Произошла ошибка при анализе товара с искусственным интеллектом.
Попробуйте повторить через несколько минут."""
            await self.send_message(chat_id, error_msg)
            return False
    
    async def send_professional_results(self, chat_id, product_data, analysis, risk_data):
        # Основной результат
        esolll_ai_analysis = analysis.get("esolll_ai_analysis", {})
        esolll_score = esolll_ai_analysis.get("esolll_score", {})
        emotional_profile = esolll_ai_analysis.get("emotional_profile", {})
        
        summary = f"""🤖 **ESOLLL AI PROFESSIONAL ANALYSIS**

📦 **{product_data['name'][:50]}...**
🏷️ {product_data['brand']} | ⭐ {product_data['rating']}/5 | 💰 {product_data['price']} ₽

{risk_data['decision_emoji']} **ESOLLL AI РЕШЕНИЕ: {risk_data['decision']}**

📋 {risk_data['decision_reason']}"""

        if risk_data.get('esolll_ai_influence'):
            summary += f"\n🤖 **ESOLLL AI оценка: {risk_data.get('esolll_ai_rating', 'N/A')}/10**"
        
        summary += f"""

🆕 **PROFESSIONAL AI ВОЗМОЖНОСТИ:**
• 🧠 Семантический анализ с ESOLLL AI Engine
• 💭 Эмоциональная аналитика покупателей
• 🔮 AI-прогнозы развития ситуации
• 📝 10 критических отзывов с детальным анализом"""
        
        await self.send_message(chat_id, summary)
        
        # ESOLLL AI инсайты
        if esolll_ai_analysis:
            ai_insights = f"""🤖 **ESOLLL AI PROFESSIONAL ИНСАЙТЫ:**

💭 **Эмоциональный профиль:**
• Общее настроение: {emotional_profile.get('overall_mood', 'нейтральный')}
• Уровень фрустрации: {emotional_profile.get('frustration_level', '5')}/10
• Риск потери лояльности: {emotional_profile.get('loyalty_risk', 'средний')}

🧠 **Что выявил ESOLLL AI:**"""
            
            ai_problems = esolll_ai_analysis.get("esolll_ai_problems", [])
            for i, problem in enumerate(ai_problems[:3], 1):
                severity = problem.get('severity', 'средняя')
                severity_emoji = "🚨" if "критическая" in severity or "высокая" in severity else "⚠️" if severity == "средняя" else "📋"
                ai_insights += f"\n{i}. {severity_emoji} **{problem.get('name', 'Проблема')}** ({severity})"
                ai_insights += f"\n   _{problem.get('description', 'Описание недоступно')[:90]}..._"
            
            await self.send_message(chat_id, ai_insights)
            
            # AI прогнозы и рекомендации
            predictions = esolll_ai_analysis.get("esolll_predictions", {})
            insights = esolll_ai_analysis.get("professional_insights", {})
            
            ai_recommendations = f"""🔮 **ESOLLL AI ПРОГНОЗЫ И РЕКОМЕНДАЦИИ:**

📈 **Прогноз тренда:** {predictions.get('sales_trend', 'Анализируется')}
📉 **Прогноз возвратов:** {predictions.get('return_forecast', 'Анализируется')}
👥 **Удержание клиентов:** {predictions.get('customer_retention', 'Прогнозируется')}

🎯 **Срочные действия от ESOLLL AI:**"""
            
            for action in insights.get('immediate_fixes', ['AI анализ в процессе'])[:3]:
                ai_recommendations += f"\n• {action}"
            
            ai_recommendations += f"\n\n💼 **Конкурентная позиция:** {insights.get('competitive_positioning', 'Анализируется')}"
            
            await self.send_message(chat_id, ai_recommendations)
        
        # Показываем 2 примера критических отзывов в боте
        critical_reviews = self.reporter.select_top_10_critical_reviews(analysis)
        if critical_reviews:
            examples_msg = f"""💬 **ПРИМЕРЫ КРИТИЧЕСКИХ ОТЗЫВОВ:**

**ОТЗЫВ #1** (⭐ {critical_reviews[0]['rating']}/5):
_{critical_reviews[0]['text'][:200]}..._

**Проблемы:** {', '.join([p['name'] for p in critical_reviews[0]['matched_problems'][:2]])}

---"""
            
            if len(critical_reviews) > 1:
                examples_msg += f"""

**ОТЗЫВ #2** (⭐ {critical_reviews[1]['rating']}/5):
_{critical_reviews[1]['text'][:200]}..._

**Проблемы:** {', '.join([p['name'] for p in critical_reviews[1]['matched_problems'][:2]])}"""
            
            examples_msg += f"\n\n📄 **Еще {max(0, len(critical_reviews) - 2)} подробных критических отзывов в отчете**"
            
            await self.send_message(chat_id, examples_msg)
        else:
            await self.send_message(chat_id, "💬 **Критические отзывы не найдены - товар показывает отличные результаты!**\n\n📄 **Детальный анализ качества в отчете**")
        
        # Традиционный анализ (для сравнения)
        if analysis.get('problems'):
            problems_text = "📊 **ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ (для сравнения):**\n\n"
            for i, (name, data) in enumerate(analysis['problems'][:3], 1):
                problems_text += f"**{i}. {name}** - {data['percentage']}%\n"
            
            problems_text += "\n📄 **Полный профессиональный отчет ESOLLL AI готовится...**"
            await self.send_message(chat_id, problems_text)
    
    async def create_professional_report(self, chat_id, analysis, risk_data, article_id, product_data):
        try:
            reports_dir = f"esolll_ai_professional_reports_{article_id}"
            os.makedirs(reports_dir, exist_ok=True)
            
            print(f"🤖 Создаю ESOLLL AI Professional отчет для {article_id}...")
            
            # Генерируем отчет с ESOLLL AI
            html_content = self.reporter.generate_esolll_ai_report(analysis, risk_data, article_id, product_data)
            
            report_path = os.path.join(reports_dir, f"esolll_ai_professional_report_{article_id}.html")
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            esolll_ai_analysis = analysis.get("esolll_ai_analysis", {})
            ai_status = "🤖 POWERED BY ESOLLL AI PROFESSIONAL ENGINE" if analysis.get("ai_powered") else "⚠️ БАЗОВЫЙ АНАЛИЗ (ESOLLL AI недоступен)"
            
            critical_reviews = self.reporter.select_top_10_critical_reviews(analysis)
            critical_count = len(critical_reviews)
            
            report_msg = f"""📊 **ESOLLL AI PROFESSIONAL REPORT ГОТОВ**

{ai_status}

🆕 **Профессиональные возможности отчета:**
• 🤖 Семантический анализ от ESOLLL AI Engine
• 💭 Эмоциональная аналитика покупателей
• 🔮 AI-прогнозы и профессиональные рекомендации
• 📝 {critical_count} критических отзывов с детальным анализом
• 📄 PDF экспорт для всех устройств (включая мобильные)

📱 **Мобильно-оптимизированный дизайн**
💡 *Для PDF: Кнопка "Скачать PDF" в отчете*"""
            
            if esolll_ai_analysis:
                ai_rating = esolll_ai_analysis.get("esolll_score", {}).get("product_rating", "N/A")
                mood = esolll_ai_analysis.get("emotional_profile", {}).get("overall_mood", "нейтральный")
                recommendation = esolll_ai_analysis.get("esolll_score", {}).get("buy_recommendation", "осторожно")
                
                ai_example = f"""🤖 **ПРИМЕР ESOLLL AI PROFESSIONAL АНАЛИЗА:**

**ESOLLL AI Оценка:** {ai_rating}/10
**Эмоциональное настроение:** {mood}
**AI Рекомендация:** {recommendation}
**Критических отзывов найдено:** {critical_count}

🧠 **Семантические проблемы выявлены автоматически**
💭 **Эмоциональный профиль покупателей построен**
📄 **Полный профессиональный анализ в отчете**"""
                await self.send_message(chat_id, ai_example)
            
            await self.send_message(chat_id, report_msg)
            await self.send_document(chat_id, report_path, f"🤖 ESOLLL AI Professional Report | {product_data['name'][:30]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка создания ESOLLL AI Professional отчета: {e}")
            
            error_msg = """❌ **Ошибка создания ESOLLL AI Professional отчета**

Произошла техническая ошибка при создании отчета с ИИ.
ESOLLL AI анализ выполнен успешно, попробуйте запросить отчет позже."""
            await self.send_message(chat_id, error_msg)
            return False
    
    async def process_message(self, message):
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        if text == '/start':
            welcome = """🤖 **ESOLLL AI Professional Analytics Engine**
*Революционная система анализа товаров с искусственным интеллектом*

**Разработчик:** Almas Kasymzhanov

🆕 **PROFESSIONAL AI ВОЗМОЖНОСТИ:**
• 🧠 **Семантический анализ** - ESOLLL AI понимает смысл отзывов
• 💭 **Эмоциональная аналитика** - анализ настроений покупателей  
• 🔮 **AI-прогнозы** - предсказание трендов и проблем
• 📝 **10 критических отзывов** - детальный анализ проблем
• 🎯 **Профессиональные рекомендации** - конкретные решения

🚀 **ЧТО ВЫ ПОЛУЧИТЕ:**
• Глубинный анализ скрытых проблем в отзывах
• Понимание реальных эмоций покупателей
• 10 самых критических отзывов с разбором
• Прогнозы развития ситуации с товаром
• Конкретные AI-рекомендации для улучшения
• Профессиональные отчеты с PDF экспортом

📝 **КАК ИСПОЛЬЗОВАТЬ:**
Отправьте артикул товара с Wildberries (6+ цифр)
Пример: 348518462

🤖 **Получите революционный анализ с ESOLLL AI Professional!**"""
            
            await self.send_message(chat_id, welcome)
        
        elif text == '/help':
            help_text = """📚 **КАК ИСПОЛЬЗОВАТЬ ESOLLL AI PROFESSIONAL**

🚀 **БЫСТРЫЙ СТАРТ:**
1. Отправьте артикул товара Wildberries (6+ цифр)
2. Дождитесь завершения AI-анализа (30-90 секунд)
3. Получите 2 примера критических отзывов в чате
4. Скачайте полный отчет с 10 отзывами и PDF экспортом

📝 **ПРИМЕРЫ АРТИКУЛОВ:**
• 348518462
• 21676342  
• 156789123

🤖 **ЧТО ВЫ ПОЛУЧИТЕ:**
• ESOLLL AI оценка товара (1-10)
• 10 самых критических отзывов с анализом
• Эмоциональный профиль покупателей
• Профессиональные рекомендации для улучшения
• PDF отчет оптимизированный для мобильных

📊 **СТРУКТУРА ОТЧЕТА:**
1. **Решение AI** - покупать/не покупать/осторожно
2. **10 критических отзывов** - полные тексты с разбором проблем
3. **ESOLLL AI инсайты** - семантический и эмоциональный анализ  
4. **Профессиональные рекомендации** - конкретные действия
5. **PDF экспорт** - сохранение для всех устройств

💡 **ПОЛЕЗНЫЕ СОВЕТЫ:**
• Лучше анализировать товары с 50+ отзывами
• Отчет адаптирован для чтения на мобильных
• Для сохранения PDF используйте кнопку в отчете
• Система работает только с русскими отзывами

📱 **МОБИЛЬНАЯ ОПТИМИЗАЦИЯ:**
• Адаптивный дизайн для телефонов и планшетов
• PDF экспорт работает на всех устройствах
• Быстрая загрузка даже при медленном интернете

🤖 **ESOLLL AI Professional Analytics Engine**
**Разработчик: Almas Kasymzhanov**"""
            
            await self.send_message(chat_id, help_text)
        
        elif text == '/info':
            info_text = """ℹ️ **О СИСТЕМЕ ESOLLL AI PROFESSIONAL**

👨‍💻 **О РАЗРАБОТЧИКЕ:**
**Алмас Касымжанов** - действующий селлер на маркетплейсах Wildberries и Kaspi.kz с опытом более 3 лет.

🎯 **ЭКСПЕРТИЗА РАЗРАБОТЧИКА:**
• Практикующий e-commerce предприниматель
• ML и AI энтузиаст-аналитик
• Специалист по анализу данных маркетплейсов  
• Эксперт по оптимизации товарных позиций
• Разработчик систем автоматизации для селлеров

🤖 **ESOLLL AI PROFESSIONAL SYSTEM:**
**ESOLLL AI Professional Analytics Engine** - революционная система анализа товаров электронной коммерции с использованием искусственного интеллекта.

🔧 **ТЕХНОЛОГИИ:**
• Машинное обучение (Machine Learning)
• Обработка естественного языка (NLP)
• Анализ настроений (Sentiment Analysis)
• Предиктивная аналитика
• Семантический анализ текстов
• Автоматическое выявление критических отзывов

📊 **СТАТИСТИКА СИСТЕМЫ:**
• Анализирует до 120 отзывов за сеанс
• Выявляет 10+ категорий проблем товаров
• Находит до 10 самых критических отзывов
• Строит детальный эмоциональный профиль покупателей
• Дает персонализированные рекомендации

🎯 **ДЛЯ КОГО ПОДХОДИТ:**
• Продавцы на маркетплейсах Wildberries, Ozon, Kaspi
• Бренды и производители товаров
• Аналитики и маркетологи e-commerce
• Инвесторы в интернет-коммерцию
• Консультанты по развитию бизнеса

🏆 **МИССИЯ ПРОЕКТА:**
Помочь селлерам и брендам принимать обоснованные решения на основе реального AI-анализа отзывов покупателей, выявляя скрытые проблемы и возможности для роста.

🤖 **ESOLLL AI Professional Analytics Engine v3.0**
**Разработчик: Алмас Касымжанов**"""
            
            await self.send_message(chat_id, info_text)
        
        else:
            article_match = re.search(r'\b\d{6,}\b', text)
            
            if article_match:
                article_id = article_match.group()
                print(f"🤖 ESOLLL AI Professional анализ артикула {article_id}")
                await self.analyze_product_professional(article_id, chat_id)
            else:
                error_message = """❌ **Отправьте артикул Wildberries**

📋 **Формат:** 6+ цифр (например: 348518462)

🤖 **Получите революционный ESOLLL AI Professional анализ:**
• 🧠 Семантический анализ отзывов с пониманием контекста
• 💭 Эмоциональная аналитика покупателей
• 📝 10 самых критических отзывов с детальным разбором
• 🔮 AI-прогнозы трендов и рисков
• 🎯 Профессиональные персонализированные рекомендации
• 📄 PDF экспорт для мобильных устройств

🚀 **ESOLLL AI Professional Analytics Engine**
**Разработчик: Almas Kasymzhanov**"""
                
                await self.send_message(chat_id, error_message)
    
    async def get_updates(self):
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{self.telegram_token}/getUpdates"
            params = {'offset': self.offset, 'timeout': 5}
            
            try:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('ok'):
                            for update in data['result']:
                                self.offset = update['update_id'] + 1
                                if 'message' in update:
                                    await self.process_message(update['message'])
                            return True
                    return False
            except:
                return True
    
    async def run_professional_bot(self, cycles=100):
        print("🤖 ЗАПУСК ESOLLL AI PROFESSIONAL ANALYTICS ENGINE")
        print("=" * 80)
        print("🏢 ESOLLL AI Professional Analytics Engine")
        print("👨‍💻 Разработчик: Almas Kasymzhanov")
        print("🤖 Powered by: Advanced AI & Machine Learning")
        print("🆕 Professional возможности:")
        print("  • 🧠 Семантический анализ отзывов")
        print("  • 💭 Эмоциональная аналитика покупателей")
        print("  • 📝 10 критических отзывов с детальным анализом")
        print("  • 🔮 AI-прогнозы и профессиональные рекомендации")
        print("  • 📄 PDF экспорт для мобильных устройств")
        print("=" * 80)
        
        self.running = True
        
        for i in range(cycles):
            if not self.running:
                break
            print(f"🔄 Цикл {i+1}/{cycles} - ESOLLL AI Professional готов к анализу")
            await self.get_updates()
            await asyncio.sleep(2)
        
        print("⏹️ ESOLLL AI Professional Bot остановлен")
    
    def stop(self):
        self.running = False

async def start_esolll_ai_professional():
    """🚀 ЗАПУСК ESOLLL AI PROFESSIONAL ANALYTICS ENGINE"""
    telegram_token = "7379556579:AAHXWwnYjcJpvTvN83nAUs04uHAykoQv-YM"
    mpstats_api_key = "68528ad55e29e6.1236050249227088a63f52d8d31984bc88a498c4"
    anthropic_api_key = "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"
    
    print("🤖 ESOLLL AI PROFESSIONAL ANALYTICS ENGINE")
    print("=" * 80)
    print("👨‍💻 Разработчик: Almas Kasymzhanov")
    print("🤖 Powered by: ESOLLL AI Professional Engine")
    print("📊 Версия: Professional Analytics - Революционная система")
    print("🆕 Professional возможности:")
    print("  • 🧠 Семантический анализ отзывов с пониманием контекста")
    print("  • 💭 Эмоциональная аналитика настроений покупателей")
    print("  • 📝 10 самых критических отзывов с детальным анализом")
    print("  • 🔮 AI-прогнозы трендов и профессиональные рекомендации")
    print("  • 📄 PDF экспорт оптимизированный для мобильных устройств")
    print("=" * 80)
    
    try:
        bot = EsolllAIProfessionalBot(telegram_token, mpstats_api_key, anthropic_api_key)
        print("\n✅ ESOLLL AI PROFESSIONAL BOT СОЗДАН!")
        print("🤖 ESOLLL AI Professional Engine интегрирован и готов")
        print("🧠 Семантический анализ отзывов активирован")
        print("💭 Эмоциональная аналитика подключена")
        print("📝 Система поиска 10 критических отзывов готова")
        print("🔮 AI-прогнозы и профессиональные рекомендации активны")
        print("📄 PDF экспорт для мобильных устройств настроен")
        print("=" * 80)
        return bot
    except Exception as e:
        print(f"❌ Ошибка создания ESOLLL AI Professional бота: {e}")
        return None

# =====================================
# 🤖 ФИНАЛЬНАЯ СЕКЦИЯ ЗАПУСКА
# =====================================

print("🤖 ESOLLL AI PROFESSIONAL ANALYTICS ENGINE ГОТОВ!")
print("=" * 80)
print("📋 КОМАНДЫ ДЛЯ ЗАПУСКА PROFESSIONAL СИСТЕМЫ:")
print()
print("# 1. Создание ESOLLL AI Professional бота:")
print("professional_bot = await start_esolll_ai_professional()")
print()
print("# 2. Запуск ESOLLL AI Professional системы:")
print("if professional_bot:")
print("    await professional_bot.run_professional_bot(100)")
print()
print("=" * 80)
print("🆕 РЕВОЛЮЦИОННЫЕ ОСОБЕННОСТИ PROFESSIONAL VERSION:")
print("• 🧠 Семантический анализ отзывов с пониманием контекста")
print("• 💭 Эмоциональная аналитика настроений покупателей")  
print("• 📝 10 самых критических отзывов с детальным анализом")
print("• 🔮 AI-прогнозы развития ситуации и профессиональные рекомендации")
print("• 🎯 Персонализированные решения на основе реальных отзывов")
print("• 📄 PDF экспорт оптимизированный для мобильных устройств")
print("• 🎨 Красивые отчеты с профессиональным дизайном")
print("• 📱 Полная адаптивность для всех устройств")
print("=" * 80)
print("🤖 Powered by ESOLLL AI Professional Analytics Engine")
print("🚀 ESOLLL AI Professional E-commerce Solutions")
print("👨‍💻 Разработчик: Almas Kasymzhanov")
# В САМОМ КОНЦЕ ФАЙЛА ДОБАВЬТЕ:
import os

async def start_esolll_ai_professional():
    """🚀 ЗАПУСК ESOLLL AI PROFESSIONAL ANALYTICS ENGINE ДЛЯ RAILWAY"""
    telegram_token = os.getenv("TELEGRAM_TOKEN", "7379556579:AAHXWwnYjcJpvTvN83nAUs04uHAykoQv-YM")
    mpstats_api_key = os.getenv("MPSTATS_API_KEY", "68528ad55e29e6.1236050249227088a63f52d8d31984bc88a498c4")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-key-here")
    
    print("🤖 ESOLLL AI PROFESSIONAL ANALYTICS ENGINE")
    print("=" * 80)
    print("👨‍💻 Разработчик: Almas Kasymzhanov")
    print("🤖 Powered by: ESOLLL AI Professional Engine")
    # ... остальной код печати ...
    
    try:
        bot = EsolllAIProfessionalBot(telegram_token, mpstats_api_key, anthropic_api_key)
        print("\n✅ ESOLLL AI PROFESSIONAL BOT СОЗДАН!")
        return bot
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    async def main():
        bot = await start_esolll_ai_professional()
        if bot:
            print("🚀 ESOLLL AI Professional Bot запущен на Railway!")
            await bot.run_professional_bot(999999)  # Для 24/7 работы
    
    asyncio.run(main())
