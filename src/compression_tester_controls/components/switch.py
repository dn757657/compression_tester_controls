

class DiPoleSwitch:
    def __init__(
            self,
            # channels_obj,
            # channels_obj_attr,
            # channel1,
            # channel2,
            name: str, 
            trigger_threshold: float,
            trigger_above_threshold: bool,
            **kwargs
    ):
        """
        switch object
        :param channel1: object attr to retrieve the float value at one switch pole
        :param channel2: object attr to retrieve the float value at other switch pole
        :param trigger_threshold: difference in channels denoting a trigger event
        :param trigger_above_threshold: is switch on above threshold
        """
        # self.channels_obj = channels_obj
        # self.channels_obj_attr = channels_obj_attr

        # self.channel1 = channel1
        # self.channel2 = channel2
        self.name = name

        self.trigger_threshold = trigger_threshold
        self.trigger_above_threshold = trigger_above_threshold

        pass

    # @property
    # def get_channel1(self):
        # adc_channel_samples = getattr(self.channels_obj, self.channels_obj_attr)
        # return adc_channel_samples[self.channel1]

    # @property
    # def get_channel2(self):
        # adc_channel_samples = getattr(self.channels_obj, self.channels_obj_attr)
        # return adc_channel_samples[self.channel2]

    def update(self, new_val: float):
        """
        sample an end stop to determine if triggered
        endstop switch could be an object also but probably not necessary
        return bool
        :param channels: must be of length 2? list of strings
        :return:
        """

        #print(f'switch_state: chan1 = {self.channel1}, chan2 = {self.channel2}')

        state = self.is_triggered(val=new_val)
        self.state = state  # update state

        return state

    def is_triggered(
            self,
            val: float
    ):
        # if abs(self.get_channel1 - self.get_channel2) > self.trigger_threshold:
        if val > self.trigger_threshold:
            if self.trigger_above_threshold == True:
                return True
            else:
                return False

        # if abs(self.get_channel1 - self.get_channel2) <= self.trigger_threshold:
        if val <= self.trigger_threshold:
            if self.trigger_above_threshold == True:
                return False
            else:
                return True
