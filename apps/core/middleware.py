from django.contrib import messages
from inertia import share


class InertiaFlashMiddleware:
    """Compartilha flash messages do Django como prop 'flash' do Inertia.

    O django.contrib.messages armazena mensagens na sessão.
    Este middleware lê as mensagens ANTES da view executar
    (elas foram setadas na request anterior, ex: messages.success no POST)
    e as compartilha via share() para que estejam disponíveis como prop.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lê as mensagens da sessão ANTES da view executar.
        # As mensagens foram criadas na request anterior (ex: POST que fez redirect).
        flash = [
            {'message': str(m), 'tags': m.tags}
            for m in messages.get_messages(request)
        ]

        if flash:
            share(request, flash=flash)

        return self.get_response(request)
