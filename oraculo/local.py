import folium
import phonenumbers
from phonenumbers import carrier
from phonenumbers import geocoder  # Importação para obter a descrição
from geopy.geocoders import Nominatim  # Importação da biblioteca Geopy
from decouple import config
import os

# Função para obter a localização e gerar o mapa
def gerar_mapa_por_numero(numero_celular):
    # Parse o número e verifica se é válido
    try:
        numero_parsed = phonenumbers.parse(numero_celular)
        if not phonenumbers.is_valid_number(numero_parsed):
            return "Número inválido."

        # Obtém a operadora
        operadora = carrier.name_for_number(numero_parsed, 'pt')

        # Obter a descrição da localização
        descricao_localizacao = geocoder.description_for_number(numero_parsed, 'pt')

        # Verifica se a descrição foi obtida
        if descricao_localizacao is None:
            return "Localização não encontrada."

        # Geocodificando a descrição da localização usando Geopy
        geolocator = Nominatim(user_agent="Number Local")
        allocation = geolocator.geocode(descricao_localizacao)

        if allocation:
            latitude = allocation.latitude
            longitude = allocation.longitude

            # Coletar detalhes da localização
            local_info = geolocator.reverse((latitude, longitude), language='pt')
            address = local_info.raw['address']
            print(address)

            cidade = address.get('city', 'Cidade não encontrada')
            bairro = address.get('suburb', 'Bairro não encontrado')
            rua = address.get('road', 'Rua/Avenida não encontrada')
            numero_residencial = address.get('house_number', '')

            # Criar a variável popup
            popup = f'Operadora: {operadora}, Localização: {descricao_localizacao}, Cidade: {cidade}, Bairro: {bairro}, Rua: {rua}, Número: {numero_residencial}'

            # Imprimir o popup no terminal
            print(popup)

            # Criar um mapa
            mapa = folium.Map(location=[latitude, longitude], zoom_start=12)
            print(mapa)

            # Adicionar um marcador para a localização
            folium.Marker(
                location=[latitude, longitude],
                popup=popup,
                icon=folium.Icon(color='blue')
            ).add_to(mapa)

            # Criar o diretório 'locali' se não existir
            if not os.path.exists('./locali'):
                os.makedirs('./locali')

            # Salvar o mapa em um arquivo HTML
            mapa_lo = "./locali/local_numero.html"
            mapa.save(mapa_lo)
            return f"Mapa gerado com sucesso: {mapa_lo}"
        else:
            return "Localização não encontrada."

    except Exception as e:
        return f"Ocorreu um erro: {e}"


# Exemplo de uso
numero_celular = "+5531996011180"  # Substitua pelo número desejado
resultado = gerar_mapa_por_numero(numero_celular)
print(resultado)