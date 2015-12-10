from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from painel.models import Painel
from parlamentares.models import Filiacao
from sapl.crud import build_crud
from sessao.models import (OrdemDia, PresencaOrdemDia, RegistroVotacao,
                           SessaoPlenaria, SessaoPlenariaPresenca,
                           VotoParlamentar)

from .models import Cronometro

cronometro_painel_crud = build_crud(
    Cronometro, '', [

        [_('Cronometro'),
         [('status', 3), ('data_cronometro', 6),
          ('tipo', 3)]],
    ])


def controlador_painel(request):

    painel_created = Painel.objects.get_or_create(data_painel=date.today())
    painel = painel_created[0]

    if request.method == 'POST':
        if 'start-painel' in request.POST:
            painel.aberto = True
            painel.save()
        elif 'stop-painel' in request.POST:
            painel.aberto = False
            painel.save()
        elif 'save-painel' in request.POST:
            painel.mostrar = request.POST['tipo_painel']
            painel.save()

    context = {'painel': painel, 'PAINEL_TYPES': Painel.PAINEL_TYPES}
    return render(request, 'painel/controlador.html', context)


def painel_view(request, pk):
    context = {'head_title': 'Painel Plenário', 'sessao_id': pk}
    return render(request, 'painel/index.html', context)


def painel_mensagem_view(request):
    return render(request, 'painel/mensagem.html')


def painel_parlamentares_view(request):
    return render(request, 'painel/parlamentares.html')


def painel_votacao_view(request):
    return render(request, 'painel/votacao.html')


def cronometro_painel(request):
    request.session[request.GET['tipo']] = request.GET['action']
    return HttpResponse({})


def get_cronometro_status(request, name):
    try:
        cronometro = request.session[name]
    except KeyError:
        cronometro = ''
    return cronometro


def get_materia_aberta(pk):
    try:
        materia = OrdemDia.objects.filter(
            sessao_plenaria_id=pk, votacao_aberta=True).first()
        return materia
    except ObjectDoesNotExist:
        return False


def get_last_materia(pk):
    try:
        materia = OrdemDia.objects.filter(
            sessao_plenaria_id=pk).order_by('-data_ordem').first()
        return materia
    except ObjectDoesNotExist:
        return None


def get_presentes(pk, response, materia):
    filiacao = Filiacao.objects.filter(
        data_desfiliacao__isnull=True, parlamentar__ativo=True)
    parlamentar_partido = {}
    for f in filiacao:
        parlamentar_partido[
            f.parlamentar.nome_parlamentar] = f.partido.sigla

    sessao_plenaria_presenca = SessaoPlenariaPresenca.objects.filter(
        sessao_plenaria_id=pk)
    presentes_sessao_plenaria = [
        p.parlamentar.nome_parlamentar for p in sessao_plenaria_presenca]
    num_presentes_sessao_plen = len(presentes_sessao_plenaria)

    presenca_ordem_dia = PresencaOrdemDia.objects.filter(
        sessao_plenaria_id=pk)
    presentes_ordem_dia = []
    for p in presenca_ordem_dia:
        nome_parlamentar = p.parlamentar.nome_parlamentar
        presentes_ordem_dia.append(
            {'id': p.id,
             'nome': nome_parlamentar,
             'partido': parlamentar_partido[nome_parlamentar],
             })
    num_presentes_ordem_dia = len(presentes_ordem_dia)

    if materia.tipo_votacao == 1:
        tipo_votacao = 'Simbólica'
    elif materia.tipo_votacao == 2:
        tipo_votacao = 'Nominal'
    elif materia.tipo_votacao == 3:
        tipo_votacao = 'Secreta'

    response.update({
        'presentes_ordem_dia': presentes_ordem_dia,
        'num_presentes_ordem_dia': num_presentes_ordem_dia,
        'presentes_sessao_plenaria': presentes_sessao_plenaria,
        'num_presentes_sessao_plenaria': num_presentes_sessao_plen,
        'status_painel': 'ABERTO',
        'msg_painel': 'Votação aberta!',
        'numero_votos_sim': 0,
        'numero_votos_nao': 0,
        'numero_abstencoes': 0,
        'total_votos': 0,
        'tipo_resultado': tipo_votacao})

    return response


def response_null_materia(response):
    response.update({
        'status_painel': 'FECHADO',
        'msg_painel': 'Nenhuma matéria disponivel para votação.'
    })
    return JsonResponse(response)


def get_votos(response, materia):
    registro = RegistroVotacao.objects.filter(
        ordem=materia, materia=materia.materia).last()
    total = (registro.numero_votos_sim +
             registro.numero_votos_nao +
             registro.numero_abstencoes)
    response.update({
        'numero_votos_sim': registro.numero_votos_sim,
        'numero_votos_nao': registro.numero_votos_nao,
        'numero_abstencoes': registro.numero_abstencoes,
        'total_votos': total,
        'tipo_resultado': registro.tipo_resultado_votacao.nome
    })
    return response


def get_votos_nominal(response, materia):
    votos = {}

    registro = RegistroVotacao.objects.get(
        ordem=materia, materia=materia.materia)

    votos_parlamentares = VotoParlamentar.objects.filter(
        votacao_id=registro.id)

    for v in votos_parlamentares:
        votos.update({v.parlamentar.id: {
            'parlamentar': v.parlamentar.nome_parlamentar,
            'voto': str(v.voto)
        }})

    total = (registro.numero_votos_sim +
             registro.numero_votos_nao +
             registro.numero_abstencoes)

    response.update({
        'numero_votos_sim': registro.numero_votos_sim,
        'numero_votos_nao': registro.numero_votos_nao,
        'numero_abstencoes': registro.numero_abstencoes,
        'total_votos': total,
        'tipo_resultado': registro.tipo_resultado_votacao.nome,
        'votos': votos
    })

    return response


def get_dados_painel(request, pk):
    sessao = SessaoPlenaria.objects.get(id=pk)
    cronometro_discurso = get_cronometro_status(request, 'discurso')
    cronometro_aparte = get_cronometro_status(request, 'aparte')
    cronometro_ordem = get_cronometro_status(request, 'ordem')

    response = {
        'sessao_plenaria': str(sessao),
        'sessao_plenaria_data': sessao.data_inicio.strftime('%d/%m/%Y'),
        'sessao_plenaria_hora_inicio': sessao.hora_inicio,
        "cronometro_aparte": cronometro_aparte,
        "cronometro_discurso": cronometro_discurso,
        "cronometro_ordem": cronometro_ordem,
    }

    materia = get_materia_aberta(pk)
    if materia:
        return JsonResponse(get_presentes(pk, response, materia))
    else:
        materia = get_last_materia(pk)
        if materia:
            if materia.resultado:
                if materia.tipo_votacao in [1, 3]:
                    return JsonResponse(
                        get_votos(get_presentes(
                            pk, response, materia), materia))
                elif materia.tipo_votacao == 2:
                    return JsonResponse(
                        get_votos_nominal(get_presentes(
                            pk, response, materia), materia))
            else:
                return JsonResponse(get_presentes(pk, response, materia))
        else:
            return response_null_materia(response)
