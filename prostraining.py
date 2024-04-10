import streamlit as st
import pandas as pd
import requests

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

def main():
    st.title("Upload e Registro de Dados de Alunos")

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
                success, fail = 0, 0
                for _, row in df.iterrows():
                    response = send_data(row, st.session_state['cookie'], "https://www.prostraining.com.br/Aluno/Salvar")
                    if response and response.status_code == 200:
                        success += 1
                    else:
                        fail += 1
                st.success(f"{success} registros enviados com sucesso.")
                if fail > 0:
                    st.error(f"{fail} registros falharam ao enviar.")

if __name__ == "__main__":
    main()
