import numpy as np
import random

class DiscreteDist(object):
	def __init__(self, pdf, seed=None):
		if np.abs(sum(pdf) - 1.0) > 0.001:
			raise ValueError('The sum of pdf is not 1')
		random.seed(seed)
		self._pdf = np.asarray(pdf)
		self._cdf = np.cumsum(self._pdf)
		self._cdf[-1] = 1.0

	def __len__(self):
		return len(self._pdf)

	@property
	def pdf(self):
		return self._pdf

	@property
	def cdf(self):
		return self._cdf

	def rv(self):
		rv = random.random()
		return int(np.searchsorted(self._cdf, rv) + 1)

class TruncatedZipf(DiscreteDist):
	def __init__(self, alpha, n, seed=None):
		if alpha <= 0:
			raise ValueError('alpha must be positive')
		if n < 0:
			raise ValueError('n must be positive')
		pdf = np.arange(1, n + 1) ** -alpha
		pdf /= np.sum(pdf)
		self._alpha = alpha
		super(TruncatedZipf, self).__init__(pdf, seed)
	@property
	def alpha(self):
		return self._alpha

def main():
	MAX=32768
	distr = TruncatedZipf(0.99, MAX)
	pdf = distr.pdf
	counter = [0] * MAX
	for i in range(0, 10000):
		idx = distr.rv()-1
		counter[idx] = counter[idx]+1
	for i in range(0, MAX):
		print ("%d: %d"%(i, counter[i]))
	for i in range(0, 10):
		print ("%d: %f"%(i, pdf[i]))

if __name__ == "__main__":
    main()

