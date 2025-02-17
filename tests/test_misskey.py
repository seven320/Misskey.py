import datetime
import uuid
from urllib.parse import urlparse

import pytest
import requests

from misskey import (
    Misskey,
    NotificationsType
)
from misskey.exceptions import (
    MisskeyAuthorizeFailedException,
    MisskeyAPIException,
)
from .conftest import TEST_HOST


@pytest.mark.parametrize('host', [
    'http://unknown-host',
    'unknown-host',
])
def test_should_connect_error_in_init(host: str):
    with pytest.raises(requests.exceptions.ConnectionError):
        Misskey(host)


@pytest.mark.parametrize('host, token', [
    (TEST_HOST, 'this_is_invalid'),
    (TEST_HOST, '')
])
def test_should_token_error_in_init(host: str, token: str):
    with pytest.raises(MisskeyAuthorizeFailedException):
        Misskey(host, i=TEST_HOST)


@pytest.mark.parametrize('host, token', [
    (TEST_HOST, 'this_is_invalid'),
    (TEST_HOST, ''),
])
def test_should_token_error_in_setter(host: str, token: str):
    with pytest.raises(MisskeyAuthorizeFailedException):
        mk = Misskey(host)
        mk.token = token


def test_address_should_be_same(mk_cli_anon: Misskey):
    host_url = urlparse(TEST_HOST)
    assert mk_cli_anon.address == host_url.netloc


def test_token_should_be_valid(
    mk_cli_user: Misskey,
    mk_user_token: str
):
    assert mk_cli_user.token == mk_user_token


def test_token_should_be_settable_and_deletable(mk_user_token: str):
    mk = Misskey(TEST_HOST)
    mk.token = mk_user_token
    assert type(mk.token) == str
    del mk.token
    assert mk.token is None


def test_should_success_i(mk_cli_user: Misskey):
    res = mk_cli_user.i()
    assert type(res) == dict


def test_should_fail_i(mk_cli_anon: Misskey):
    with pytest.raises(MisskeyAPIException) as e:
        mk_cli_anon.i()

    assert type(e.value.code) == str
    assert type(e.value.message) == str
    assert type(e.value.id) == uuid.UUID or type(e.value.id) == str


def test_meta(mk_cli_anon: Misskey):
    res = mk_cli_anon.meta()
    assert type(res) == dict


def test_stats(mk_cli_anon: Misskey):
    res = mk_cli_anon.stats()
    assert type(res) == dict


def test_i_favorites(mk_cli_admin: Misskey):
    res = mk_cli_admin.i_favorites()
    assert type(res) == list


def test_should_be_viewable_note(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str
):
    res = mk_cli_admin.notes_show(mk_admin_new_note)
    assert type(res) == dict


def test_note_poll_expires_at(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
):
    res = mk_cli_admin.notes_create(
        text='poll test (expires_at)',
        poll_choices=[
            'test 1',
            'test 2',
        ],
        poll_expires_at=(
            datetime.datetime.now() +
            datetime.timedelta(minutes=1)
        ),
    )
    assert type(res) == dict

    vote_res = mk_cli_user.notes_polls_vote(
        res['createdNote']['id'],
        0,
    )
    assert type(vote_res) == bool
    assert vote_res

    is_deleted = mk_cli_admin.notes_delete(res['createdNote']['id'])
    assert type(is_deleted) == bool
    assert is_deleted


def test_note_poll_expired_after(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
):
    res = mk_cli_admin.notes_create(
        text='poll test (expired_after)',
        poll_choices=[
            'test 1',
            'test 2',
        ],
        poll_expired_after=datetime.timedelta(minutes=1),
    )
    assert type(res) == dict

    vote_res = mk_cli_user.notes_polls_vote(
        res['createdNote']['id'],
        0,
    )
    assert type(vote_res) == bool
    assert vote_res

    is_deleted = mk_cli_admin.notes_delete(res['createdNote']['id'])
    assert type(is_deleted) == bool
    assert is_deleted


def test_should_be_error_in_create_note_visibility(
    mk_cli_admin: Misskey,
):
    with pytest.raises(ValueError):
        mk_cli_admin.notes_create(visibility='not valid visibility')


def test_i_notifications(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.i_notifications(
        include_types={
            NotificationsType.REACTION
        },
    )
    assert type(res) == list


def test_notifications_mark_all_as_read(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.notifications_mark_all_as_read()
    assert type(res) == bool
    assert res


def test_should_be_error_in_i_notifications(
    mk_cli_admin: Misskey,
):
    with pytest.raises(ValueError):
        mk_cli_admin.i_notifications(
            include_types=[
                'unknown_type'
            ]
        )

    with pytest.raises(ValueError):
        mk_cli_admin.i_notifications(
            exclude_types=[
                'unknown_type'
            ]
        )


def test_should_can_be_pin_and_unpin_note(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res_pin = mk_cli_admin.i_pin(mk_admin_new_note)
    assert type(res_pin) == dict
    res_unpin = mk_cli_admin.i_unpin(mk_admin_new_note)
    assert type(res_unpin) == dict


def test_should_ok_show_replies(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_renotes(mk_admin_new_note)
    assert type(res) == list


def test_should_ok_show_reactions(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_reactions(
        mk_admin_new_note,
        reaction_type='✅',
    )
    assert type(res) == list


def test_should_can_be_reaction_to_notes(
    mk_cli_user: Misskey,
    mk_admin_new_note: str,
):
    res_reaction = mk_cli_user.notes_reactions_create(
        mk_admin_new_note,
        '✅',
    )
    assert type(res_reaction) == bool
    assert res_reaction
    res_del_reaction = mk_cli_user.notes_reactions_delete(
        mk_admin_new_note,
    )
    assert type(res_del_reaction) == bool
    assert res_del_reaction


def test_notes_timeline(
    mk_cli_admin: Misskey,
):
    timeline = mk_cli_admin.notes_timeline(
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now() +
            datetime.timedelta(hours=3)
        )
    )
    assert type(timeline) == list


def test_notes_local_timeline(
    mk_cli_admin: Misskey,
):
    timeline_local = mk_cli_admin.notes_local_timeline(
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now() +
            datetime.timedelta(hours=3)
        )
    )
    assert type(timeline_local) == list


def test_notes_hybrid_timeline(
    mk_cli_admin: Misskey,
):
    timeline_hybrid = mk_cli_admin.notes_hybrid_timeline(
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now() +
            datetime.timedelta(hours=3)
        )
    )
    assert type(timeline_hybrid) == list


def test_notes_global_timeline(
    mk_cli_admin: Misskey,
):
    timeline_global = mk_cli_admin.notes_global_timeline(
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now() +
            datetime.timedelta(hours=3)
        )
    )
    assert type(timeline_global) == list


def test_notes_replies(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_replies(mk_admin_new_note)
    assert type(res) == list


def test_renote_note(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_create(
        renote_id=mk_admin_new_note,
    )
    assert type(res) == dict

    res_unrenote = mk_cli_admin.notes_unrenote(
        mk_admin_new_note,
    )
    assert type(res_unrenote) == bool
    assert res_unrenote


def test_favorite_note(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res_favorite = mk_cli_admin.notes_favorites_create(
        mk_admin_new_note,
    )
    assert type(res_favorite) == bool
    assert res_favorite

    res_unfav = mk_cli_admin.notes_favorites_delete(
        mk_admin_new_note,
    )
    assert type(res_unfav) == bool
    assert res_unfav


def test_notes_conversation(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_conversation(
        mk_admin_new_note,
    )
    assert type(res) == list


def test_notes_children(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_children(
        mk_admin_new_note,
    )
    assert type(res) == list


def test_announcements(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.announcements()
    assert type(res) == list


def test_notes_watching(
    mk_cli_user: Misskey,
    mk_admin_new_note: str,
):
    res_watch = mk_cli_user.notes_watching_create(
        mk_admin_new_note,
    )
    assert type(res_watch) == bool
    assert res_watch
    res_unwatch = mk_cli_user.notes_watching_delete(
        mk_admin_new_note,
    )
    assert type(res_unwatch) == bool
    assert res_unwatch


def test_notes_state(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_state(
        mk_admin_new_note,
    )
    assert type(res) == dict


def test_i_update(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.i_update(
        name='Unit test user admin',
        birthday=datetime.date.today(),
        lang='ja-JP',
        muting_notification_types=[
            'app',
        ],
    )
    assert type(res) == dict


def test_users_show(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.users_show(
        username='user',
    )
    assert type(res) == dict


def test_users_following(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.users_following(
        username='user'
    )
    assert type(res) == list


def test_users_followers(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.users_followers(
        username='user'
    )
    assert type(res) == list


def test_user_notes(
    mk_cli_admin: Misskey,
    mk_admin_id: str,
):
    res = mk_cli_admin.users_notes(
        mk_admin_id,
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now()
        ),
    )
    assert type(res) == list


def test_users_stats(
    mk_cli_admin: Misskey,
    mk_admin_id: str,
):
    res = mk_cli_admin.users_stats(
        mk_admin_id,
    )
    assert type(res) == dict


def test_user_relation(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_single = mk_cli_admin.users_relation(
        mk_user_id,
    )
    assert type(res_single) == dict
    res_multiple = mk_cli_admin.users_relation(
        [mk_user_id],
    )
    assert type(res_multiple) == list


def test_following(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_follow = mk_cli_admin.following_create(
        mk_user_id,
    )
    assert type(res_follow) == dict
    res_unfollow = mk_cli_admin.following_delete(
        mk_user_id,
    )
    assert type(res_unfollow) == dict


def test_follow_request(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
    mk_user_id: str,
    mk_admin_id: str,
):
    mk_cli_user.i_update(
        is_locked=True,
    )
    mk_cli_admin.following_create(
        mk_user_id,
    )
    res_follow_cancel = mk_cli_admin.following_requests_cancel(
        mk_user_id,
    )
    assert type(res_follow_cancel) == dict

    mk_cli_admin.following_create(
        mk_user_id,
    )
    res_follow_list = mk_cli_user.following_requests_list()
    assert type(res_follow_list) == list
    res_follow_reject = mk_cli_user.following_requests_reject(
        mk_admin_id,
    )
    assert type(res_follow_reject) == bool
    assert res_follow_reject

    mk_cli_admin.following_create(
        mk_user_id,
    )
    res_follow_accept = mk_cli_user.following_requests_accept(
        mk_admin_id,
    )
    assert type(res_follow_accept) == bool
    assert res_follow_accept

    mk_cli_user.i_update(
        is_locked=False,
    )
    mk_cli_admin.following_delete(
        mk_user_id,
    )


def test_should_fail_in_drives_files_create(
    mk_cli_anon: Misskey
):
    with pytest.raises(MisskeyAPIException):
        with open('tests/test_image.png', mode='rb') as f:
            mk_cli_anon.drive_files_create(
                f,
            )


def test_drive(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.drive()
    assert type(res) == dict


def test_drive_stream(
    mk_cli_admin: Misskey,
):
    res_stream = mk_cli_admin.drive_stream()
    assert type(res_stream) == list

    res_files = mk_cli_admin.drive_files()
    assert type(res_files) == list

    res_folders = mk_cli_admin.drive_folders()
    assert type(res_folders) == list


def test_drive_files(
    mk_cli_admin: Misskey
):
    with open('tests/test_image.png', mode='rb') as f:
        res_create = mk_cli_admin.drive_files_create(
            f,
        )
        assert type(res_create) == dict

        res_file_check = mk_cli_admin.drive_files_check_existence(
            res_create['md5'],
        )
        assert type(res_file_check) == bool
        assert res_file_check

        res_find_hash = mk_cli_admin.drive_files_find_by_hash(
            res_create['md5'],
        )
        assert type(res_find_hash) == list

        res_attached_notes = mk_cli_admin.drive_files_attached_notes(
            res_create['id'],
        )
        assert type(res_attached_notes) == list

        res_files_show = mk_cli_admin.drive_files_show(
            res_create['id'],
        )
        assert type(res_files_show) == dict

        res_files_update = mk_cli_admin.drive_files_update(
            res_create['id'],
            folder_id=None,
            comment='test file',
        )
        assert type(res_files_update) == dict

        res_delete = mk_cli_admin.drive_files_delete(
            res_create['id'],
        )
        assert type(res_delete) == bool
        assert res_delete


def test_drive_folders(
    mk_cli_admin: Misskey,
):
    res_create = mk_cli_admin.drive_folders_create(
        name='test-folder',
    )
    assert type(res_create) == dict

    res_show = mk_cli_admin.drive_folders_show(
        res_create['id'],
    )
    assert type(res_show) == dict

    res_update = mk_cli_admin.drive_folders_update(
        folder_id=res_create['id'],
        name='renamed-folder',
        parent_id=None,
    )
    assert type(res_update) == dict

    res_delete = mk_cli_admin.drive_folders_delete(
        res_create['id'],
    )
    assert type(res_delete) == bool
    assert res_delete


def test_users_report_abuse(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res = mk_cli_admin.users_report_abuse(
        user_id=mk_user_id,
        comment='this is test report abuse',
    )
    assert type(res) == bool
    assert res


def test_mute(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_mute = mk_cli_admin.mute_create(
        mk_user_id,
    )
    assert type(res_mute) == bool
    assert res_mute

    res_mute_list = mk_cli_admin.mute_list()
    assert type(res_mute_list) == list

    res_unmute = mk_cli_admin.mute_delete(
        mk_user_id,
    )
    assert type(res_unmute) == bool
    assert res_unmute


def test_blocking(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_block = mk_cli_admin.blocking_create(
        mk_user_id,
    )
    assert type(res_block) == dict

    res_block_list = mk_cli_admin.blocking_list()
    assert type(res_block_list) == list

    res_unblock = mk_cli_admin.blocking_delete(
        mk_user_id,
    )
    assert type(res_unblock) == dict


def test_users_lists(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_create = mk_cli_admin.users_lists_create(
        'test-list',
    )
    assert type(res_create) == dict

    res_show = mk_cli_admin.users_lists_show(
        res_create['id'],
    )
    assert type(res_show) == dict

    res_list = mk_cli_admin.users_lists_list()
    assert type(res_list) == list

    res_push = mk_cli_admin.users_lists_push(
        list_id=res_create['id'],
        user_id=mk_user_id,
    )
    assert type(res_push) == bool
    assert res_push

    res_pull = mk_cli_admin.users_lists_pull(
        list_id=res_create['id'],
        user_id=mk_user_id,
    )
    assert type(res_pull) == bool
    assert res_pull

    res_update = mk_cli_admin.users_lists_update(
        list_id=res_create['id'],
        name='test-list-renamed',
    )
    assert type(res_update) == dict

    res_delete = mk_cli_admin.users_lists_delete(
        res_create['id'],
    )
    assert type(res_delete) == bool
    assert res_delete
