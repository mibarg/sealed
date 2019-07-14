import pickle

from sealed import CipherScheme


def test_scheme_pickle():
    cs_1 = CipherScheme()

    cs_2 = pickle.loads(pickle.dumps(cs_1))

    assert cs_1 == cs_2


def test_keys_pickle():
    cs = CipherScheme()
    pk_1, sk_1 = cs.generate_keys()

    _ = pickle.loads(pickle.dumps(pk_1))
    _ = pickle.loads(pickle.dumps(sk_1))


def test_cipher_pickle(plain=7, base=2):
    cs = CipherScheme()
    pk, sk = cs.generate_keys()

    e_1 = cs.encrypt(pk, plain, base)
    e_2 = pickle.loads(pickle.dumps(e_1))

    assert cs.decrypt(sk, e_2) == plain