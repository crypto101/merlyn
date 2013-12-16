"""Note: this is horribly insecure; only listen on localhost ever!

"""
from twisted.cred import portal
from twisted.conch import manhole, manhole_ssh


def makeFactory(store, ampFactory):
    shellGlobals = {"store": store, "ampFactory": ampFactory}
    makeManhole = lambda _ign: manhole.ColoredManhole(shellGlobals)

    realm = manhole_ssh.TerminalRealm()
    realm.chainedProtocolFactory.protocolFactory = makeManhole

    p = portal.Portal(realm, [])
    return manhole_ssh.ConchFactory(p)
