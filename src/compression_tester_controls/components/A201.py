import logging
import numpy as np

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


# TODO need to add force conversion - maybe store the cal curve as json and pass it in to use
class A201:
    def __init__(
            self,
            name: str,
            vout_plus,
            vout_neg,
            vref_plus,
            vref_neg,
            rf: float = 0
            ) -> None:
        
        self.name == name

        self._vout_plus = vout_plus
        self._vout_neg = vout_neg
        self._vref_plus = vref_plus
        self._vref_neg = vref_neg
        
        self.vout = None
        self.vref = None

        self.rs = None
        self.load = None

        logging.info(f"A201 Flexiforce initialized with Rf Value: {self.rf}\n")
        if self.rf == 0:
            logging.info(f"MEASUREMENTS INVALID - NO RF PROVIDED")

        pass
    
    def _update_channels(self, n_samples: int = None):
        """
        add n samples to define a running average
        """
        if n_samples:
            self.vout = np.average(self._vout_plus.sample_n(n=n_samples) - self._vout_neg.sample_n(n=n_samples))
            self.vref = np.average(self._vref_plus.sample_n(n=n_samples) - self._vref_neg.sample_n(n=n_samples))
        else:
            self.vout = self._vout_plus.sample() - self._vout_neg.sample()
            self.vref = self._vref_plus.sample() - self._vref_neg.sample()

        pass

    def _update_rs(self):
        try:
            self.rs = self.rf/((self.vout/self.vref) - 1)
        except ZeroDivisionError:
            self.rs = 0
        pass

    def _update_load(self):
        self.load = self.rs * 1
        pass

    def _update(self, n_samples: int = None):
        self._update_channels(n_samples=n_samples)
        self._update_rs()
        self._update_load()
        pass

    def sample(self, n_samples: int = None):
        self._update(n_samples=n_samples)
        return self.load, self.rs
    
    def determine_rf(self, rs: float):
        """
        pass in known rs to determine adjustable rf pot resistance
        """
        try:
            self.rf = rs * ((self.vout/self.vref) - 1)
        except ZeroDivisionError:
            self.rf = None
        return self.rf        

