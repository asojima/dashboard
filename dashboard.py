import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="📊 Дашборд продаж",
    page_icon="📈",
    layout="wide"
)

API_URL = "http://localhost:8000"

# Стилизация
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
    }
    .login-form {
        padding: 2rem;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Инициализация сессии
if 'token' not in st.session_state:
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.login_time = None

# Функция для выхода
def logout():
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.login_time = None
    st.rerun()

# ==================== СТРАНИЦА ЛОГИНА ====================
if st.session_state.token is None:
    st.title("🔐 Авторизация")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            
            with st.form("login_form"):
                st.subheader("Вход в систему")
                username = st.text_input("👤 Логин", placeholder="Введите логин")
                password = st.text_input("🔑 Пароль", type="password", placeholder="Введите пароль")
                
                submitted = st.form_submit_button("🚀 Войти", use_container_width=True)
                
                if submitted:
                    if not username or not password:
                        st.warning("⚠️ Заполните все поля")
                    else:
                        with st.spinner("Проверка данных..."):
                            try:
                                response = requests.post(
                                    f"{API_URL}/login",
                                    json={"username": username, "password": password},
                                    timeout=5
                                )
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    st.session_state.token = data['access_token']
                                    st.session_state.username = data['username']
                                    st.session_state.login_time = datetime.now()
                                    st.success(f"✅ Добро пожаловать, {username}!")
                                    st.rerun()
                                else:
                                    st.error("❌ Неверный логин или пароль!")
                            except requests.exceptions.ConnectionError:
                                st.error("❌ Бэкенд не запущен! Запусти: uvicorn main:app --reload")
                            except Exception as e:
                                st.error(f"❌ Ошибка: {str(e)}")
            
            st.markdown("---")
            st.info("💡 **Тестовые пользователи:**\n\n- `admin` / `admin123` (администратор)\n- `user` / `user123` (пользователь)")
            st.markdown("📝 **Или создайте нового пользователя через** `/register`")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# ==================== ДАШБОРД ====================
# Если авторизован - показываем дашборд
headers = {"Authorization": f"Bearer {st.session_state.token}"}
session = requests.Session()
session.headers.update(headers)

# Верхняя панель
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title(f"📊 Дашборд продаж")
    st.caption(f"👋 Привет, **{st.session_state.username}**!")
with col2:
    if st.button("🔄 Обновить", use_container_width=True):
        st.rerun()
with col3:
    if st.button("🚪 Выйти", use_container_width=True):
        logout()

st.divider()

# Проверка соединения
try:
    response = session.get(f"{API_URL}/sales/my_profile", timeout=3)
    if response.status_code != 200:
        st.error("❌ Сессия истекла. Войдите заново.")
        logout()
        st.stop()
except:
    st.error("❌ Бэкенд не отвечает! Проверь: uvicorn main:app --reload")
    st.stop()

# Карточки статистики
try:
    stats = session.get(f"{API_URL}/sales/stats").json()
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "💰 Общая выручка", 
        f"${stats['total_revenue']:,.2f}",
        delta=f"${stats['avg_order_value']:,.2f} средний чек"
    )
    col2.metric("📦 Всего заказов", stats['total_orders'])
    col3.metric("📈 Средний чек", f"${stats['avg_order_value']:,.2f}")
    
    # Количество уникальных товаров
    all_sales = session.get(f"{API_URL}/sales?limit=1000").json()
    unique_products = len(set([s['product'] for s in all_sales]))
    col4.metric("🏷️ Уникальных товаров", unique_products)
    
    st.divider()
except Exception as e:
    st.warning(f"⚠️ Не удалось загрузить статистику: {str(e)}")

# Таблица
st.subheader("📋 Последние продажи")
tab1, tab2 = st.tabs(["📊 Таблица", "📈 Графики"])

with tab1:
    data = session.get(f"{API_URL}/sales?limit=50").json()
    df = pd.DataFrame(data)
    
    # Форматирование даты
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Фильтры
    col1, col2 = st.columns(2)
    with col1:
        if 'category' in df.columns:
            categories = ['Все'] + list(df['category'].unique())
            selected_category = st.selectbox("Фильтр по категории", categories)
            if selected_category != 'Все':
                df = df[df['category'] == selected_category]
    with col2:
        if 'product' in df.columns:
            products = ['Все'] + list(df['product'].unique())
            selected_product = st.selectbox("Фильтр по товару", products)
            if selected_product != 'Все':
                df = df[df['product'] == selected_product]
    
    st.dataframe(df, use_container_width=True, height=400)
    
    # Кнопка экспорта
    if st.button("📥 Экспорт в CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Скачать CSV",
            data=csv,
            file_name=f"sales_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Выручка по категориям")
        cat_data = session.get(f"{API_URL}/sales/by_category").json()
        df_cat = pd.DataFrame(cat_data)
        if not df_cat.empty:
            fig = px.pie(
                df_cat, 
                values='total', 
                names='category',
                title='Распределение выручки',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных для отображения")
    
    with col2:
        st.subheader("🏆 Топ-10 товаров")
        top_data = session.get(f"{API_URL}/sales/top_products?limit=10").json()
        df_top = pd.DataFrame(top_data)
        if not df_top.empty:
            fig2 = px.bar(
                df_top, 
                x='product', 
                y='total_sold',
                title='Количество проданных единиц',
                color='total_sold',
                color_continuous_scale='Viridis'
            )
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Нет данных для отображения")
    
    # Дополнительный график
    st.subheader("📊 Детальный анализ")
    col3, col4 = st.columns(2)
    
    with col3:
        # Распределение по ценам
        df_all = pd.DataFrame(session.get(f"{API_URL}/sales?limit=1000").json())
        if not df_all.empty:
            fig3 = px.histogram(
                df_all, 
                x='price', 
                nbins=20,
                title='Распределение цен на товары',
                color='category'
            )
            st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        # Топ по выручке
        df_all['revenue'] = df_all['price'] * df_all['quantity']
        top_revenue = df_all.groupby('product')['revenue'].sum().sort_values(ascending=False).head(10).reset_index()
        if not top_revenue.empty:
            fig4 = px.bar(
                top_revenue,
                x='product',
                y='revenue',
                title='Топ-10 по выручке',
                color='revenue',
                color_continuous_scale='Reds'
            )
            fig4.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig4, use_container_width=True)

# Footer
st.divider()
st.caption(f"🔐 Защищенный дашборд | Пользователь: {st.session_state.username} | Сессия активна: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")