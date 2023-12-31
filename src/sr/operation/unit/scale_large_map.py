import time
from typing import ClassVar

from basic import Point, Rect
from basic.i18_utils import gt
from basic.img import MatchResult, cv2_utils
from basic.log_utils import log
from sr.context import Context
from sr.operation import Operation


class ScaleLargeMap(Operation):

    rect: ClassVar[Rect] = Rect(600, 960, 1040, 1020)

    def __init__(self, ctx: Context, scale: int):
        """
        默认在大地图页面 点击缩放按钮
        :param scale: 缩放次数。负数为缩小，正数为放大
        """
        super().__init__(ctx, 5,op_name=gt('缩放地图 %d', 'ui') % scale)
        self.scale: int = scale
        self.click_times = 0
        self.pos = None

    def _execute_one_round(self) -> int:
        if self.pos is None:
            self.pos = self.get_click_pos()

        if self.pos is not None:
            log.info('准备缩放地图 点击 %s %s', self.pos.center,
                     self.ctx.controller.click(self.pos.center))
            time.sleep(0.5)
            self.click_times += 1
            if self.click_times == abs(self.scale):
                return Operation.SUCCESS
            else:
                return Operation.WAIT
        else:
            return Operation.RETRY

    def get_click_pos(self) -> MatchResult:
        screen = self.screenshot()
        template_id = 'plus' if self.scale > 0 else 'minus'
        x1, y1 = ScaleLargeMap.rect.left_top.tuple()
        source, _ = cv2_utils.crop_image(screen, ScaleLargeMap.rect)
        result = self.ctx.im.match_template(source, template_id, template_type='origin')
        if result.max is not None:
            result.max.x += x1
            result.max.y += y1
        return result.max

    def on_resume(self):
        self.pos = self.get_click_pos()
        super().on_resume()
