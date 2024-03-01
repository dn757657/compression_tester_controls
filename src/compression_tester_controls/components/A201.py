import logging
import math
import numpy as np

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


# TODO need to add force conversion - maybe store the cal curve as json and pass it in to use
class A201:
    def __init__(
            self,
            name: str,
            exp_A: float,
            exp_B: float,
            rf: float = 0,
            **kwargs
            ) -> None:
        """
        exp A and B are constants in the exponential function fit to the force measurement
        for translating resistance to force
        """


        self.name = name
        self.rf = rf
        self.rs = None
        self.load = None

        self.exp_a_const = exp_A
        self.exp_b_const = exp_B

        logging.info(f"A201 Flexiforce initialized with Rf Value: {self.rf}")
        if self.rf == 0:
            logging.info(f"MEASUREMENTS INVALID - NO RF PROVIDED")

        pass
    
    # def _update_channels(self, n_samples: int = None):
    #     """
    #     add n samples to define a running average
    #     """
    #     if n_samples:
    #         self.vout = np.average(self._vout_plus.sample_n(n=n_samples) - self._vout_neg.sample_n(n=n_samples))
    #         self.vref = np.average(self._vref_plus.sample_n(n=n_samples) - self._vref_neg.sample_n(n=n_samples))
    #     else:
    #         self.vout = self._vout_plus.sample() - self._vout_neg.sample()
    #         self.vref = self._vref_plus.sample() - self._vref_neg.sample()

    #     pass

    def _update_rs(self, vout: float, vref: float):
        try:
            self.rs = self.rf/((vout / vref) - 1)
        except ZeroDivisionError:
            self.rs = 0
        pass
    
    def get_rs(self, vout: float, vref: float):
        self._update_rs(vout=vout, vref=vref)
        return self.rs

    def _update_load(self, vout: float, vref: float):
        self._update_rs(vout=vout, vref=vref)
        try:
            self.load = (self.exp_a_const * np.exp((1/self.rs) * self.exp_b_const))
        except ZeroDivisionError:
            self.load = 0
        pass

    def get_load(self, vout: float, vref: float):
        self._update_load(vout=vout, vref=vref)
        return self.load

    # def _update_load(self):
    #     self.load = self.rs * 1
    #     pass

    # def _update(self, n_samples: int = None):
    #     self._update_channels(n_samples=n_samples)
    #     self._update_rs()
    #     self._update_load()
    #     pass

    # def sample(self, n_samples: int = None):
    #     self._update(n_samples=n_samples)

    #     print(f"{self.name} Vout: {self.vout}")
    #     print(f"{self.name} Vref: {self.vref}")

    #     return self.load, self.rs
    
    def get_rf(self, rs: float, vout: float, vref: float):
        """
        pass in known rs to determine adjustable rf pot resistance
        """
        try:
            rf = rs * ((vout/vref) - 1)
        except ZeroDivisionError:
            rf = None
        return rf        

