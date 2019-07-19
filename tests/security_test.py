import pytest
import pickle

from sealed.models import CipherScheme
from sealed.primitives import *


def test_same_keygen_different_keys(plain=1):
    """
    Repeated called to CipherScheme generate_key() generate matching keys
    """
    cs = CipherScheme()

    # created from the same KeyGenerator
    pk_1, sk_1 = cs.generate_keys()
    pk_2, sk_2 = cs.generate_keys()

    cipher_1 = cs.encrypt(pk_1, plain)
    cipher_2 = cs.encrypt(pk_2, plain)

    # both sets of keys work
    assert plain == cs.decrypt(sk_1, cipher_1)
    assert plain == cs.decrypt(sk_2, cipher_1)
    assert plain == cs.decrypt(sk_1, cipher_2)
    assert plain == cs.decrypt(sk_2, cipher_2)


def test_different_keygen_same_context(plain=1):
    """
    Using two different KeyGenerators generate non-matching keys
    """
    cs = CipherScheme()
    context = cs._context

    key_gen_1 = KeyGenerator(context)
    key_gen_2 = KeyGenerator(context)

    # created from a different KeyGenerator
    pk_1, sk_1 = key_gen_1.public_key(), key_gen_1.secret_key()
    pk_2, sk_2 = key_gen_2.public_key(), key_gen_2.secret_key()

    cipher_1 = cs.encrypt(pk_1, plain)
    cipher_2 = cs.encrypt(pk_2, plain)

    # using same KeyGen generated keys works
    assert plain == cs.decrypt(sk_1, cipher_1)
    assert plain == cs.decrypt(sk_2, cipher_2)

    # using keys from a different KeyGen doesn't work
    assert plain != cs.decrypt(sk_1, cipher_2)
    assert plain != cs.decrypt(sk_2, cipher_1)


@pytest.mark.parametrize("second_context", ("from_pickle", "regenerate", "from_cipher", "from_encoder"))
def different_context(second_context, plain=1):
    cs_1 = CipherScheme()

    if second_context == "from_pickle":
        cs_2 = pickle.loads(pickle.dumps(cs_1))
    elif second_context == "regenerate":
        cs_2 = CipherScheme()
    elif second_context == "from_cipher":
        # steal context from CipherText
        pk, _ = cs_1.generate_keys()
        cipher = cs_1.encrypt(pk, plain)
        context = cipher._context

        cs_2 = CipherScheme()
        cs_2._context = context
        cs_2._keygen = KeyGenerator(context)
        cs_2._evl = Evaluator(context)
    elif second_context == "from_encoder":
        # steal context from Encoder
        pk, _ = cs_1.generate_keys()
        cipher = cs_1.encrypt(pk, plain)
        context = cipher._encoder._context

        cs_2 = CipherScheme()
        cs_2._context = context
        cs_2._keygen = KeyGenerator(context)
        cs_2._evl = Evaluator(context)
    else:
        return

    pk_1, sk_1 = cs_1.generate_keys()
    pk_2, sk_2 = cs_2.generate_keys()

    cipher_1 = cs_1.encrypt(pk_1, plain)
    cipher_2 = cs_2.encrypt(pk_2, plain)

    # different CipherSchemes can be used, but not only with keys generated from the original CipherScheme
    assert plain == cs_2.decrypt(sk_1, cipher_1)
    assert plain == cs_1.decrypt(sk_2, cipher_2)

    # keys generated by another CipherScheme won't work
    assert plain != cs_1.decrypt(sk_2, cipher_1)
    assert plain != cs_2.decrypt(sk_1, cipher_2)

    # keys generated by another CipherScheme won't work, even when using the CipherScheme that generated them
    assert plain != cs_2.decrypt(sk_2, cipher_1)
    assert plain != cs_1.decrypt(sk_1, cipher_2)
