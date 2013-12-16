"""Note: this is horribly insecure; only listen on localhost ever!

"""
from twisted.cred import checkers, portal
from twisted.conch import manhole, manhole_ssh

checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(manhole="manhole")


def makeFactory(store, ampFactory):
    shellGlobals = {"store": store, "ampFactory": ampFactory}
    makeManhole = lambda _ign: manhole.ColoredManhole(shellGlobals)

    realm = manhole_ssh.TerminalRealm()
    realm.chainedProtocolFactory.protocolFactory = makeManhole

    p = portal.Portal(realm, [checker])
    return manhole_ssh.ConchFactory(p)
