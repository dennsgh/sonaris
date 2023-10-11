from pages import factory
import time


def check_connection(args_dict: dict) -> bool:

    if my_generator is not None:
        is_alive = factory.get_dg4202(args_dict)
        if not is_alive:
            factory.dg_last_alive = None
            my_generator = None
        # device is alive.
        # transition from dead to alive None -> time
        if factory.dg_last_alive is None:
            factory.dg_last_alive = time.time()
        return is_alive
    # connection is dead from here
    factory.dg_last_alive = None