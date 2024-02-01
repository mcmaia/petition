import altair as alt
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
# with open('../config.yaml') as file:
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

# st.set_page_config(
#         page_title="Controle de Abaixo Assinados", page_icon="⬇", layout="centered"
#     )

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Olá, *{name}*')
    
    @st.cache_data
    def get_data():
        source = pd.DataFrame([
            {
                "admin_id" : 1,
                "id": 1,
                "user_id": 101,
                "petition_name": "Reestatização da CEEE",
                "text_petition": "We demand immediate action to protect the rainforests. Deforestation is destroying vital ecosystems and accelerating climate change. Sign this petition to urge policymakers to take decisive measures to save our planet's lungs.",
                "image": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA/ElEQVQ4T7XTvU4CQRDG8YYKj0LwiKRoBzrAh4cBC/MEIiCFFjgYwEDyQUkEE0pAxR+BIRu+8YHkP1t5nXvdmZw7lz3F8xV+3Nz99+L/HxHwGSh/s6Ic0N4e/BL9T5ARZtRmPqCTAzsD+3xWCYYomM5m2XbDn0UnszM29jLc7+TXyI7h7dXHUNjZ+VgkHAAjyFfUu84FAuBhNDbFQGgA43QzKFKgNgQtATOC0wFIAj2DTC0j2gWgENsVBoDgIrWqBGc+5vWzxBcsBlDKEUKQEWgiwVewPwBA7H0tHaK9b2lv6D1Wt+Bz6+KgAAAABJRU5ErkJggg==",
                "signature_count" : 120000,
                "create_date" : "2024-01-23"
            },
            {
                "admin_id" : 1,
                "id": 2,
                "user_id": 101,
                "petition_name": "Salve os Yanomani",
                "text_petition": "Single-use plastics are polluting our oceans and harming marine life. We call on governments to enact legislation banning single-use plastics and promoting sustainable alternatives. Join us in the fight against plastic pollution!",
                "image": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAATklEQVQ4T2NkoBAwUqifAWjwApg0WBWcQjMUmBZgWlABIQj4Q1G8UIULCyBGpCDsgpGNIhGjAGAwZKMwIsArf4GlDzBgAAAABJRU5ErkJggg==",
                "signature_count" : 160000,
                "create_date" : "2024-01-23"
            },
            {
                "admin_id" : 1,
                "id": 3,
                "user_id": 103,
                "petition_name": "Fora Bolsonaro",
                "text_petition": "It's time to transition to renewable energy sources and leave fossil fuels behind. Renewable energy is clean, sustainable, and essential for combating climate change. Sign this petition to show your support for a greener future!",
                "image": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAT0lEQVQ4T2NkoBAwUqifAWjwApg0WBWcQjMUmBZgWlABIQj4Q1G8UIULCyBGpCDsgpGNIhGjAGAwZKMwIsArf4GlDzBgAAAABJRU5ErkJggg==",
                "signature_count" : 130000,
                "create_date" : "2024-01-23"
            }
            ])
        return source


    @st.cache_data(ttl=60 * 60 * 24)
    def get_chart(data):
        hover = alt.selection_point(
            fields=["id"],
            nearest=True,
            on="mouseover",
            empty=False,
        )

        bars = (
            alt.Chart(data, height=500, title="Acompanhamento de abaixo-assinados")
            #.mark_line()
            .mark_bar()
            .encode(
                x=alt.X("petition_name", title="Nome da campanha"),
                y=alt.Y("signature_count", title="Assinaturas").sort('y'),
            )
        )

        # Draw points on the line, and highlight based on selection
        points = bars.transform_filter(hover).mark_circle(size=65)

        # Draw a rule at the location of the selection
        tooltips = (
            alt.Chart(data)
            .mark_rule()
            .encode(
                x="petition_name",
                y="signature_count",
                opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                tooltip=[
                    alt.Tooltip("create_date", title="Data criação"),
                    alt.Tooltip("user_id", title="Usuário"),
                    alt.Tooltip("signature_count", title="Quantidade de Assinaturas"),
                ],
            )
            .add_params(hover)
        )

        return (bars + points + tooltips).interactive() 


    # Original time series chart. Omitted `get_chart` for clarity
    source = get_data()
    chart = get_chart(source)


    # Display both charts together
    st.altair_chart((chart).interactive(), use_container_width=True)
elif authentication_status == False:
    st.error('Usuário e/ou Senha estão incorretos')
elif authentication_status == None:
    st.warning('Por favor preencha seu nome de usuário e senha')
