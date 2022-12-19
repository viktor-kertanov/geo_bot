from db_handlers.mongo_db import (user_voted, get_flag_img_rating,
                                  get_or_create_user)


def test_user_voted_true(mongodb):
    assert user_voted(
        mongodb,
        'data/country_images_aux/niger_flag.jpeg',
        1670826777
    ) is True


def test_user_voted_false(mongodb):
    assert user_voted(
        mongodb,
        'data/country_images_aux/niger_flag.jpeg',
        1670826999
    ) is False


def test_get_flag_img_rating(mongodb):
    assert get_flag_img_rating(
        mongodb, 'data/country_images_aux/andorra_flag.jpeg'
    ) == 3
    assert get_flag_img_rating(
        mongodb, 'data/country_images_aux/no_flag.jpeg'
    ) == 0


def test_get_or_create_user(mongodb, effective_user):
    user_exist = mongodb.users.find_one({'user_id': effective_user.id})
    assert user_exist is None
    user = get_or_create_user(mongodb, effective_user,  777)
    user_exist = mongodb.users.find_one({'user_id': effective_user.id})
    assert user == user_exist
