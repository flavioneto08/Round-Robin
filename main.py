import matplotlib.pyplot as plt
import numpy as np
import time

def ler_arquivo_entrada(filePath):
    with open(filePath, 'r') as file:
        processos = []
        for line in file:
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            fileInfo = {
                'pid': parts[0],
                'duracao': int(parts[1]),
                'chegada': int(parts[2]),
                'op_io': [int(t) for t in parts[3].split(',')] if len(parts) > 3 else [],
                'aux_io': 0,
                'flag_io': False,
                'duracao_original': int(parts[1]),
                'tempo_espera': 0
            }
            processos.append(fileInfo)
    return processos

def update_grafico(dados_gantt, ax, cores, processo_para_y, tempo_total):
    ax.clear()
    ax.set_xlim(0, tempo_total)
    ax.set_ylim(0, len(processo_para_y))

    for pid, times in dados_gantt.items():
        for start, duration in times:
            ax.broken_barh([(start, duration)], (processo_para_y[pid], 0.9), facecolors=cores[pid])

    ax.set_yticks(list(processo_para_y.values()))
    ax.set_yticklabels(list(processo_para_y.keys()))
    ax.set_xticks(np.arange(0, tempo_total + 1, 1))
    ax.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5) 
    ax.set_xlabel('Tempo')
    ax.set_ylabel('Processos')
    ax.set_title('Gráfico de Gantt - Escalonador Round Robin')

def round_robin(processos, quantum, output_file, dados_gantt, ax, cores, processo_para_y):
    tempo_total = sum(processo['duracao'] for processo in processos)
    fila_processos = []
    fila_cpu = []
    aux_quantum = 0
    novos_processos = []

    tempos_espera = {processo['pid']: 0 for processo in processos}
    #tempos_executados = {processo['pid']: 0 for processo in processos}
    #tempos_inicio = {processo['pid']: -1 for processo in processos}

    for i in range(tempo_total + 1):
        output_file.write(f"************* TEMPO {i} ************\n")
        for processo in processos:
            if processo['chegada'] == i:
                novos_processos.append(processo)
                output_file.write(f"#[evento] CHEGADA <{novos_processos[0]['pid']}>\n")
                
        if i == 0:
            if len(novos_processos) > 0:        
                fila_cpu.append(novos_processos[0])
                novos_processos.pop(0)
                if len(fila_cpu[0]['op_io']) > 0:
                    fila_cpu[0]['aux_io'] += 1
                    fila_cpu[0]['flag_io'] = False
                aux_quantum += 1    
                output_file.write(f"CPU: {fila_cpu[0]['pid']}({fila_cpu[0]['duracao']})\n")
                #tempos_inicio[fila_cpu[0]['pid']] = i
            else:
                continue   
        else:
            if len(fila_processos) == 0 and len(fila_cpu) == 0:
                if len(novos_processos) > 0:
                    fila_cpu.append(novos_processos[0])
                    novos_processos.pop(0)
                    if len(fila_cpu[0]['op_io']) > 0:
                        fila_cpu[0]['aux_io'] += 1
                        fila_cpu[0]['flag_io'] = False
                    aux_quantum += 1
                    output_file.write(f"CPU: {fila_cpu[0]['pid']}({fila_cpu[0]['duracao']})\n")
                    #tempos_inicio[fila_cpu[0]['pid']] = i
                else:
                    continue
                
            if len(fila_cpu) != 0:
                
                if fila_cpu[0]['duracao'] > 0:
                    fila_cpu[0]['duracao'] -= 1
                    #tempos_executados[fila_cpu[0]['pid']] += 1
                    
                if any(fila_cpu[0]['aux_io'] == io for io in fila_cpu[0]['op_io']) and fila_cpu[0]['flag_io'] == False:
                    fila_cpu[0]['flag_io'] = True
                    fila_processos.append(fila_cpu[0])
                    fila_cpu.pop(0)
                    output_file.write(f"#[evento] OPERACAO I/O <{fila_processos[-1]['pid']}>\n")
                    aux_quantum = 0    
                
            if aux_quantum == quantum:
                fila_processos.append(fila_cpu[0])
                fila_cpu.pop(0)
                output_file.write(f"#[evento] FIM QUANTUM <{fila_processos[-1]['pid']}>\n")
                aux_quantum = 0

            if len(fila_cpu) == 0:
                if len(fila_processos) == 0:
                    continue
                else:
                    fila_cpu.append(fila_processos[0])
                    fila_processos.pop(0)
                    if len(fila_cpu[0]['op_io']) > 0:
                        fila_cpu[0]['aux_io'] += 1
                        fila_cpu[0]['flag_io'] = False
                    aux_quantum += 1    
                    output_file.write(f"CPU: {fila_cpu[0]['pid']}({fila_cpu[0]['duracao']})\n")
                    #tempos_inicio[fila_cpu[0]['pid']] = i
                    
            else:
                if (fila_cpu[0]['duracao'] == 0):
                    output_file.write(f"#[evento] ENCERRADO <{fila_cpu[0]['pid']}>\n")
                    fila_cpu.pop(0)
                    if len(fila_processos) == 0:
                        output_file.write("FILA: Não há processos na fila\n")
                        output_file.write("ACABARAM OS PROCESSOS!\n")
                        break
                    else:
                        fila_cpu.append(fila_processos[0])
                        output_file.write(f"CPU: {fila_cpu[0]['pid']}({fila_cpu[0]['duracao']})\n")
                        fila_processos.pop(0)
                        aux_quantum = 0
                        aux_quantum += 1
                        if len(fila_cpu[0]['op_io']) > 0:
                            fila_cpu[0]['aux_io'] += 1
                            fila_cpu[0]['flag_io'] = False
                else:
                    output_file.write(f"CPU: {fila_cpu[0]['pid']}({fila_cpu[0]['duracao']})\n")
                    if len(fila_cpu[0]['op_io']) > 0:
                        fila_cpu[0]['aux_io'] += 1
                        fila_cpu[0]['flag_io'] = False
                    aux_quantum += 1

        if len(fila_cpu) > 0:
            pid_atual = fila_cpu[0]['pid']
            if dados_gantt[pid_atual] and dados_gantt[pid_atual][-1][0] + dados_gantt[pid_atual][-1][1] == i:
                dados_gantt[pid_atual][-1] = (dados_gantt[pid_atual][-1][0], dados_gantt[pid_atual][-1][1] + 1)
            else:
                dados_gantt[pid_atual].append((i, 1))

        update_grafico(dados_gantt, ax, cores, processo_para_y, tempo_total)
        plt.pause(0.1)
        time.sleep(1)

        for novoProcesso in novos_processos:
            fila_processos.append(novoProcesso)
            novos_processos.pop()

        if fila_processos:
            fila_str = "FILA: " + " ".join(f"{proc['pid']}({proc['duracao']})" for proc in fila_processos)
        else:
            fila_str = "FILA: Não há processos na fila"
        output_file.write(fila_str + "\n")

        for processo in fila_processos:
            tempos_espera[processo['pid']] += 1

    total_tempo_espera = 0
    print("\nTempos de espera:")
    for processo in processos:
        tempo_espera = tempos_espera[processo['pid']]
        print(f"{processo['pid']}: {tempo_espera}")
        total_tempo_espera += tempo_espera
    
    tempo_espera_medio = total_tempo_espera / len(processos)
    print(f"Tempo de espera médio: {tempo_espera_medio:.1f}")

    return dados_gantt

def main():
    filePath = '.\\arquivo_teste.txt'
    outputPath = '.\\resultado_simulacao.txt'
    processos = ler_arquivo_entrada(filePath)
    quantum = 4
    fig, ax = plt.subplots(figsize=(12, 6))

    processos_ids = sorted(set(processo['pid'] for processo in processos))
    processo_para_y = {processo: i for i, processo in enumerate(processos_ids)}

    cores = {processo: np.random.rand(3,) for processo in processos_ids}
    dados_gantt = {processo: [] for processo in processos_ids}

    print(f"Quantum usado = {quantum}")

    with open(outputPath, 'w') as output_file:
        output_file.write("***********************************\n")
        output_file.write("***** ESCALONADOR ROUND ROBIN *****\n")
        output_file.write("-----------------------------------\n")
        output_file.write("------- INICIANDO SIMULAÇÃO -------\n")
        output_file.write("-----------------------------------\n")
        round_robin(processos, quantum, output_file, dados_gantt, ax, cores, processo_para_y)
        output_file.write("-----------------------------------\n")
        output_file.write("------- ENCERRANDO SIMULAÇÃO ------\n")
        output_file.write("-----------------------------------\n")

    print("A simulação foi concluída com sucesso e o resultado foi salvo em 'resultado_simulacao.txt'.")
    fig.savefig('.\\gantt_chart.png', bbox_inches='tight')
    plt.show()
    
main()
