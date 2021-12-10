# ESR-TP3

* Announcement port - 23456
* Data port - 65432

## Packet
* type-4bytes;ipdestino-4bytes;port-4bytes;payload-1024bytes


## payload
### Announcement
* table


# TODO
* fazer cancelamento de rotas
* Criar thread a ler de uma fila de packets para imprimir
* adicionar forma de saber se pipe foi quebrada
* linha 210 - recv handler and sendall handler