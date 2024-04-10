import streamlit as st
import pandas as pd
import requests
from io import BytesIO


# Função para realizar o login e obter o cookie
def login(url, data):
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.prostraining.com.br/Login",
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        cookies = response.cookies.get_dict()
        return cookies.get('ProS.AuthCookie', '')
    else:
        return None

# Função para enviar os dados de cada aluno
def send_data(row, cookie_value, url):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"ProS.AuthCookie={cookie_value}"
    }
    data = row_to_data(row)
    response = requests.post(url, headers=headers, data=data)
    return response

# Função para mapear uma linha do DataFrame para os dados da requisição
def row_to_data(row):
    # Ajuste esta função para mapear os dados corretamente
    return {
        'alunoviewmodel[IdAluno]': row['IdAluno'],
        'alunoviewmodel[IdCategoriaPretendida]': row['IdCategoriaPretendida'],
        'alunoviewmodel[Pessoa][Nome]': row['Nome'],
        'alunoviewmodel[Pessoa][Cpf]': row['Cpf'],
        'alunoviewmodel[Pessoa][DataNascimento]': row['DataNascimento'],
        'alunoviewmodel[Pessoa][Email]': row['Email'],
        'alunoviewmodel[Pessoa][Endereco][CEP]': row['CEP'],
        'alunoviewmodel[Pessoa][Endereco][IdUF]': row['IdUF'],
        'alunoviewmodel[Pessoa][Endereco][IdMunicipio]': row['IdMunicipio'],
        'alunoviewmodel[Pessoa][Endereco][Logradouro]': row['Logradouro'],
        'alunoviewmodel[Pessoa][Endereco][Numero]': row['Numero'],
        'alunoviewmodel[Pessoa][Endereco][Bairro]': row['Bairro'],
        'alunoviewmodel[Pessoa][IdCategoriaHabilitacao]': row['IdCategoriaHabilitacao'],
        'alunoviewmodel[Pessoa][Genero]': row['Genero'],
        # Continue adicionando campos conforme necessário
    }
# Função de gerar planilha
def generate_excel_model():
    # Definindo o modelo da planilha como um DataFrame
    modelo_df = pd.DataFrame({
        'IdAluno': [""],
        'IdCategoriaPretendida': [""],
        'Nome': [""],
        'Cpf': [""],
        'DataNascimento': [""],
        'Email': [""],
        'CEP': [""],
        'IdUF': [""],
        'IdMunicipio': [""],
        'Logradouro': [""],
        'Numero': [""],
        'Bairro': [""],
        'IdCategoriaHabilitacao': [""],
        'Genero': [""],
        # Adicione mais colunas conforme necessário
    })

    # Convertendo o DataFrame em um arquivo Excel em memória
    towrite = BytesIO()
    modelo_df.to_excel(towrite, index=False)

    towrite.seek(0)  # Retornando ao início do BytesIO para leitura
    
    return towrite
# URL do logotipo
logo_url = "https://www.prostraining.com.br/Content/img/logotipo/logo-prostraining.svg"

def main():
    st.image(logo_url, width=400)
    st.title("Cadastro em lote")
    # Gerar e oferecer o modelo de planilha para download
    file_bytes = generate_excel_model()
    st.download_button(label="Download Modelo de Planilha",
                       data=file_bytes,
                       file_name="modelo_planilha.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with st.form("login_form", clear_on_submit=False):
        id_empresa = st.text_input("ID da Empresa", "")
        usuario = st.text_input("Usuário", "")
        senha = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Login")

    if submit_button:   
        url_login = "https://www.prostraining.com.br/Login/SignIn"
        data_login = {
            "IdEmpresa": id_empresa,
            "Login": usuario,
            "Senha": senha,
            "Tipo": "1"
        }
        cookie_value = login(url_login, data_login)
        if cookie_value:
            st.success("Login realizado com sucesso!")
            st.text(f"Cookie Capturado: {cookie_value}")  # Exibe o cookie capturado
            st.session_state['cookie'] = cookie_value
        else:
            st.error("Falha no login. Por favor, verifique suas credenciais.")

    if 'cookie' in st.session_state and st.session_state['cookie']:
        uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xlsx")
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            if st.button('Enviar Dados'):
                for index, row in df.iterrows():
                    response = send_data(row, st.session_state['cookie'], "https://www.prostraining.com.br/Aluno/Salvar")
                    if response and response.status_code == 200:
                        # Exibe uma mensagem de sucesso para cada aluno registrado com sucesso
                        st.success(f"Registro {index + 1} ({row['Nome']}) enviado com sucesso.")
                    else:
                        # Você também pode mostrar falhas, se desejar
                        st.error(f"Registro {index + 1} ({row['Nome']}) falhou ao enviar.")

if __name__ == "__main__":
    main()
