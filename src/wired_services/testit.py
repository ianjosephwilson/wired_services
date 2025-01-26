import wired_services.services
from wired import ServiceRegistry
import venusian
from .interfaces import ISettings

def run_tests(container):
    from .interfaces import IHello, FancyHelloABC, IHelloAgain

    hello_api = container.get(IHello)
    print (hello_api.hello())

    hello_again_api = container.get(IHelloAgain)
    print (hello_again_api.hello())

    fancy_hello_api = container.get(FancyHelloABC)
    print (fancy_hello_api.hello('Ian'))


def bootstrap_services():
    registry = ServiceRegistry()
    scanner = venusian.Scanner(registry=registry)
    scanner.scan(wired_services.services, categories=('wired_service',))
    settings_dict = {
        'hello.prefix': 'Greetings to you!',
        'hello.local_tz_offset_hours': -8,
        'hello.lucky_max_number': 999
    }
    registry.register_singleton(settings_dict, ISettings)
    return registry.create_container()


if __name__ == '__main__':
    container = bootstrap_services()
    run_tests(container)
