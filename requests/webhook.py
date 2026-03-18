import streamlit as st
# ...existing code...
    elif body['event'] == 'transaction_failed':
        # Tratar o erro da transação
        transaction_id = body['data']['transaction_id']
        print(f'Transação {transaction_id} falhou!')
    else:
        print(f'Evento desconhecido: {body["event"]}')

    # Retornar uma resposta OK
    return Response(status_code=status.HTTP_200_OK)
