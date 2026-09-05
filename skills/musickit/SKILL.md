---
name: musickit
description: "Integrate Apple Music catalog, playback, and personal library using MusicKit. Use when requesting MusicKit authorization, searching the catalog, playing songs/albums/playlists, checking subscription status, offering subscription sheets, or managing user playlists."
---

# MusicKit

Access the Apple Music catalog, play tracks, query personal cloud libraries, and present subscription upsells using MusicKit. Targets Swift 6.3 / iOS 26+.

## Contents

- [Setup & Permissions](#setup--permissions)
- [Subscription Verification](#subscription-verification)
- [Catalog Search & Browse](#catalog-search--browse)
- [Audio Playback](#audio-playback)
- [Subscription Upsell](#subscription-upsell)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Setup & Permissions

Add `NSAppleMusicUsageDescription` to Info.plist. Request user authorization:

```swift
import MusicKit

func requestMusicAccess() async -> MusicAuthorization.Status {
    let status = await MusicAuthorization.request()
    return status
}
```

## Subscription Verification

Check capabilities on `MusicSubscription.current` before offering catalog playback:

```swift
func verifySubscription() async -> Bool {
    let sub = try? await MusicSubscription.current
    return sub?.canPlayCatalogContent ?? false
}
```

## Catalog Search & Browse

Search Apple Music songs, albums, and artists:

```swift
func searchMusic(term: String) async throws -> MusicItemCollection<Song> {
    var request = MusicCatalogSearchRequest(term: term, types: [Song.self])
    request.limit = 20
    let response = try await request.response()
    return response.songs
}

func fetchCharts() async throws -> MusicItemCollection<Song> {
    let request = MusicCatalogChartsRequest(types: [Song.self])
    let response = try await request.response()
    return response.songs.first?.items ?? []
}
```

## Audio Playback

Use `ApplicationMusicPlayer` for app-scoped playback or `SystemMusicPlayer` for system-wide Music app playback:

```swift
let player = ApplicationMusicPlayer.shared

func playSong(_ song: Song) async throws {
    player.queue = [song]
    try await player.play()
}
```

## Subscription Upsell

Present the native subscription sheet when `canBecomeSubscriber` is true:

```swift
import SwiftUI
import MusicKit

struct MusicView: View {
    @State private var showOffer = false

    var body: some View {
        Button("Subscribe to Apple Music") {
            showOffer = true
        }
        .musicSubscriptionOffer(isPresented: $showOffer)
    }
}
```

## Common Mistakes

- **Playing catalog songs without checking subscription**: Fails or plays previews unless `subscription.canPlayCatalogContent` is true.
- **Missing NSAppleMusicUsageDescription**: Instant crash on calling `MusicAuthorization.request()`.
- **Using SystemMusicPlayer when app-scoped audio is needed**: `SystemMusicPlayer` replaces the user's active Music app queue. Use `ApplicationMusicPlayer.shared` for in-app music.
- **Forgetting playback error handling**: Playback can fail due to parental restrictions, offline status, or DRM. Catch errors from `player.play()`.
- **Hardcoding storefront IDs**: MusicKit automatically infers the current storefront from user account settings; avoid hardcoding country codes.

## Review Checklist

- [ ] `NSAppleMusicUsageDescription` added to Info.plist
- [ ] `MusicAuthorization.request()` handled before library/playback calls
- [ ] `subscription.canPlayCatalogContent` verified prior to full track streaming
- [ ] `musicSubscriptionOffer` provided for non-subscribers
- [ ] Appropriate player selected (`ApplicationMusicPlayer` vs `SystemMusicPlayer`)

## References

- Extended patterns (custom playlists, Now Playing metadata, audio engine integration): [references/musickit-patterns.md](references/musickit-patterns.md)
- [MusicKit framework](https://sosumi.ai/documentation/musickit)
- [MusicAuthorization](https://sosumi.ai/documentation/musickit/musicauthorization)
- [ApplicationMusicPlayer](https://sosumi.ai/documentation/musickit/applicationmusicplayer)
- [MusicCatalogSearchRequest](https://sosumi.ai/documentation/musickit/musiccatalogsearchrequest)
- [MusicSubscription](https://sosumi.ai/documentation/musickit/musicsubscription)
- [canPlayCatalogContent](https://sosumi.ai/documentation/musickit/musicsubscription/canplaycatalogcontent)
- [canBecomeSubscriber](https://sosumi.ai/documentation/musickit/musicsubscription/canbecomesubscriber)
- [hasCloudLibraryEnabled](https://sosumi.ai/documentation/musickit/musicsubscription/hascloudlibraryenabled)
- [MusicCatalogChartsRequest initializer](https://sosumi.ai/documentation/musickit/musiccatalogchartsrequest/init(genre:kinds:types:))
- [musicSubscriptionOffer(isPresented:options:onLoadCompletion:)](https://sosumi.ai/documentation/swiftui/view/musicsubscriptionoffer(ispresented:options:onloadcompletion:))
- [MPRemoteCommandCenter](https://sosumi.ai/documentation/mediaplayer/mpremotecommandcenter)
- [MPNowPlayingInfoCenter](https://sosumi.ai/documentation/mediaplayer/mpnowplayinginfocenter)
- [NSAppleMusicUsageDescription](https://sosumi.ai/documentation/bundleresources/information-property-list/nsapplemusicusagedescription)
