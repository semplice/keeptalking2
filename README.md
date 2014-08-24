keeptalking2
============

Keeptalking2 is a library to interface with the internationalization features of the distribution.  
It provides a public API that can be used to set/get the Keyboard layout, locale and timezone, as well as
get a list of the supported ones.

Keeptalking2 is the Python3 port of [keeptalking](https://github.com/semplice/keeptalking).

While you can easily run the legacy keeptalking in Python3, it will not be supported.

Changes from keeptalking
------------------------

keeptalking2 dropt the gtk/cli frontends. Keeptalking2 is API-compatible with the legacy version though, so
it's possible to port the old frontends to the new library.

In addition, the t9n library has been removed as well. For translations, it's recommended to switch to
[quickstart](https://github.com/semplice/quickstart).

The set/get methods now rely on localed and timedated, which are part of systemd.  
It's possible to use the old, init system agnostic methods by using the 'offline' versions.

For example,

	kb = keeptalking2.Keyboard.Keyboard()
	print(kb.default) # Uses localed via DBus
	print(kb.default_offline) # Looks at /etc/default/keyboard, like the legacy keeptalking

Currently keeptalking2 does **NOT** check for the existence of the DBus services,
and thus can't transparently fallback to the offline variants.

Please note that for techinical reasons it's not possible to change the internationalization
settings of another system using the "online" methods.
The eventual specified target will not be used when using those methods.

You need to use the offline variants for that.
