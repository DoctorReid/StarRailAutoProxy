import sr.app.world_patrol
from sr.app import world_patrol_app
from sr.app.world_patrol_app import WorldPatrol
from sr.context import Context, get_context


def _test_load_all_route():
    print('目前总共 %d 条路线' % len(sr.app.world_patrol.load_all_route_id()))


def _test_run_one_route():
    ctx.init_all(renew=True)
    ctx.start_running()
    ctx.controller.init()
    app.first = False
    app.run_one_route('P02_R03_R01')


if __name__ == '__main__':
    ctx: Context = get_context()
    app = WorldPatrol(ctx)
    _test_load_all_route()