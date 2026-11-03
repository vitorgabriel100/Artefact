"""Expose deterministic development tools with backward-compatible CLI aliases."""

import argparse
import json

from .catalog import Catalog
from .config import data_directory
from .policies import Policies


def main() -> None:
    """Parse one command, query the supplied snapshot and print JSON evidence."""
    parser = argparse.ArgumentParser(description='Empório da Música development tools')
    parser.add_argument('--data', default=str(data_directory()), help='Source data directory')
    subcommands = parser.add_subparsers(dest='command', required=True)

    # Mantemos os aliases porque a versão anterior já foi validada no Windows.
    search = subcommands.add_parser('catalog', aliases=['catalogo'], help='Search products')
    search.set_defaults(action='catalog')
    search.add_argument('--query', '--busca', dest='query', default='')
    search.add_argument('--category', '--categoria', dest='category', default='')
    search.add_argument('--max-price', '--maximo', dest='max_price')
    search.add_argument('--payment', '--pagamento', dest='payment',
                        choices=['table', 'pix'], default='table')

    product = subcommands.add_parser('product', aliases=['produto'], help='Inspect one product')
    product.set_defaults(action='product')
    product.add_argument('id', type=int)
    product.add_argument('--payment', '--pagamento', dest='payment',
                         choices=['table', 'pix'], default='table')

    policy = subcommands.add_parser('policy', aliases=['politica'], help='Retrieve policy pages')
    policy.set_defaults(action='policy')
    policy.add_argument('query')
    args = parser.parse_args()

    if args.action == 'policy':
        result = Policies(args.data).search(args.query)
    else:
        catalog = Catalog(args.data)
        try:
            if args.action == 'product':
                result = catalog.product(args.id, args.payment)
            else:
                result = catalog.search(args.query, args.category, args.max_price,
                                        payment=args.payment)
        finally:
            # A conexão precisa fechar também quando uma consulta lança uma exceção.
            catalog.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
