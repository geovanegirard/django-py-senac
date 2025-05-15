import mysql.connector

def conecta_no_banco_de_dados():
    cnx = mysql.connector.connect(host='127.0.0.1', user='root', password='')

    cursor = cnx.cursor()
    cursor.execute('SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = "aulaDjango";')
    num_results = cursor.fetchone()[0]
    cursor.close()

    if num_results > 0:
        print('O banco de dados aulaDjango existe e está pronto para uso.')
    else:
        cursor = cnx.cursor()
        cursor.execute('CREATE DATABASE aulaDjango;')
        cnx.commit()
        cursor.close()

        cnx.database = 'aulaDjango'

        cursor = cnx.cursor()
        cursor.execute('CREATE TABLE contatos (id_contato INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, mensagem TEXT NOT NULL, situacao VARCHAR(50) NOT NULL);')
        cursor.execute('CREATE TABLE usuarios (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), email VARCHAR(255), senha VARCHAR(255));')
        
       
        cursor.execute('CREATE TABLE placar (contatos INT NOT NULL, vitorias INT DEFAULT 0, derrotas INT DEFAULT 0, PRIMARY KEY (contatos), FOREIGN KEY (contatos) REFERENCES contatos(id_contato) ON DELETE CASCADE);')

        cnx.commit()
        cursor.close()

    try:
        bd = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='aulaDjango'
        )
    except mysql.connector.Error as err:
        print("Erro de conexão com o banco de dados:", err)
        raise

    return bd
