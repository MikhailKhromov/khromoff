# file with static shit we need in processing


def static_context(request):
    context = {'static': {
        # TODO: rename to https
        'HOSTNAME': 'https://' + request.META['HTTP_HOST'],
        'urls': {'MY_VK': 'https://vk.com/id516131573',
                 'MY_TELEGRAM': 'https://t.me/Mikhail_Khromov',
                 'MY_GITHUB': 'https://github.com/mikhailkhromov'
                 }
    }}
    return context


