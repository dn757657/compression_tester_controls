

class DiPoleSwitch:
    def __init__(
            self,
            channel1,
            channel2,
            trigger_threshold: float,
            trigger_above_threshold: bool,
    ):
        """
        switch object
        :param channel1: object attr to retrieve the float value at one switch pole
        :param channel2: object attr to retrieve the float value at other switch pole
        :param trigger_threshold: difference in channels denoting a trigger event
        :param trigger_above_threshold: is switch on above threshold
        """
        self.channel1 = channel1
        self.channel2 = channel2

        self.trigger_threshold = trigger_threshold
        self.trigger_above_threshold = trigger_above_threshold

        self.state = self.read()

        pass

    def read(self):
        """
        sample an end stop to determine if triggered
        endstop switch could be an object also but probably not necessary
        return bool
        :param channels: must be of length 2? list of strings
        :return:
        """

        print(f'{abs(self.channel1 - self.channel2)}')

        # TODO need to set state in here? - no outside since we need to know the direction
        # the motor is going to know which endstop state to set

        state = self.is_triggered()
        self.state = state  # update state

        return state

    def is_triggered(
            self
    ):
        if abs(self.channel1 - self.channel2) > self.trigger_threshold:
            if self.trigger_above_threshold == True:
                return True
            else:
                return False

        if abs(self.channel1 - self.channel2) <= self.trigger_threshold:
            if self.trigger_above_threshold == True:
                return False
            else:
                return True