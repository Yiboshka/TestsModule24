from api import PetFriends
from settings import valid_email, valid_password, not_valid_password, not_valid_email
import os
import pytest

pf = PetFriends()
youshallnotpass = [('Бобо', '><', '-5'),]


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """Проверка получения ключа"""
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """Проверка получения списка питомцев"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_simple(name='Бобо', animal_type='львенок',
                                     age='2'):
    """Проверка добавления питомца без фото"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name


def test_add_new_pet_with_photo(name='Чжань', animal_type='кролик',
                                     age='4', pet_photo='images/zhanzhan.jpg'):
    """Проверка добавления профиля питомца с фото"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_with_photo(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name


def test_successful_set_photo(pet_photo='images/zhg.jpg'):
    """Проверка изменения фото в профиле питомца"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)
        assert status == 200
        assert result['pet_photo'] is not None
    else:
        raise Exception("В списке нет питомцев")


def test_successful_delete_self_pet():
    """Проверка функции удаления питомца"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_simple(auth_key, "Bobo", "львенок", "2")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Бобо', animal_type='львенок', age=2):
    """Проверяем возможность обновления информации о питомце"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("В списке нет питомцев")


@pytest.mark.parametrize('name, animal_type, age', youshallnotpass)
def test_negative_add_pet_simple(name, animal_type, age):
    """Проверка того, что нельзя создать питомца с некорректными данными"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    assert status == 400
    assert result['name'] is None


def test_negative_get_api_key(email=not_valid_email, password=not_valid_password):
    """Проверка того, что нельзя получить ключ незарегистрированным пользователям"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_negative_get_pets_list_all(filter=''):
    """Проверка того, что нельзя получить список питомцев используя некорректный ключ"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    auth_key['key'] += '1'
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403


@pytest.mark.parametrize('name, animal_type, age', youshallnotpass)
def test_negative_update_self_pet_info(name, animal_type, age):
    """Проверка обновления информации о питомце с некорректными данными."""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pf.add_new_pet_simple(auth_key, name, animal_type, age)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 400
        assert result is None
    else:
        raise Exception("В списке нет питомцев")
