import argparse
import json
from .catalog import Catalog
from .policies import Policies


def main():
    parser = argparse.ArgumentParser(description='Ferramentas do protótipo Empório da Música')
    parser.add_argument('--data',default='data')
    sub = parser.add_subparsers(dest='command',required=True)
    search = sub.add_parser('catalogo')
    search.add_argument('--busca',default='')
    search.add_argument('--categoria',default='')
    search.add_argument('--maximo')
    search.add_argument('--pagamento',choices=['table','pix'],default='table')
    product = sub.add_parser('produto')
    product.add_argument('id',type=int)
    product.add_argument('--pagamento',choices=['table','pix'],default='table')
    policy = sub.add_parser('politica')
    policy.add_argument('query')
    args = parser.parse_args()
    if args.command == 'politica':
        result = Policies(args.data).search(args.query)
    else:
        catalog = Catalog(args.data)
        try:
            result = (catalog.product(args.id,args.pagamento) if args.command == 'produto' else
                      catalog.search(args.busca,args.categoria,args.maximo,payment=args.pagamento))
        finally:
            catalog.close()
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
