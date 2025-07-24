import 'dart:math';

import 'package:amplify_flutter/amplify_flutter.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import 'package:localgaid_mobile/components/audio_guide_card.dart';
import 'package:localgaid_mobile/domain_models/audio_guide.dart';
import 'package:localgaid_mobile/domain_models/place.dart';
import 'package:localgaid_mobile/repositories/place_repository.dart';
import 'package:localgaid_mobile/utils.dart';

class PlaceDetailScreen extends StatefulWidget {
  final int placeId;
  final PlaceRepository placeRepository;

  const PlaceDetailScreen({
    super.key,
    required this.placeId,
    required this.placeRepository,
  });

  @override
  State<PlaceDetailScreen> createState() => _PlaceDetailScreenState();
}

class _PlaceDetailScreenState extends State<PlaceDetailScreen> {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<(Place, List<AudioGuide>)>(
      future: widget.placeRepository.getPlace(id: widget.placeId),
      builder:
          (
            BuildContext context,
            AsyncSnapshot<(Place, List<AudioGuide>)> snapshot,
          ) {
            if (snapshot.hasData) {
              final (place, audioGuides) =
                  snapshot.data as (Place, List<AudioGuide>);
              return _PlaceDetailView(place: place, audioGuides: audioGuides);
            } else if (snapshot.hasError) {
              return Scaffold(
                body: Padding(
                  padding: EdgeInsets.all(8),
                  child: Center(
                    child: const Icon(
                      Icons.error_outline,
                      color: Colors.red,
                      size: 60,
                    ),
                  ),
                ),
              );
            } else {
              return Scaffold(
                body: Padding(
                  padding: EdgeInsets.all(8),
                  child: Center(
                    child: SizedBox(
                      width: 60,
                      height: 60,
                      child: CircularProgressIndicator(),
                    ),
                  ),
                ),
              );
            }
          },
    );
  }
}

class _PlaceDetailView extends StatefulWidget {
  final Place place;
  final List<AudioGuide> audioGuides;

  const _PlaceDetailView({required this.place, required this.audioGuides});

  @override
  State<_PlaceDetailView> createState() => __PlaceDetailViewState();
}

class __PlaceDetailViewState extends State<_PlaceDetailView> {
  final CarouselController controller = CarouselController(initialItem: 1);
  final player = AudioPlayer();

  AudioGuide? currentAudioGuide;
  int currentPlayTime = 0;

  @override
  void initState() {
    super.initState();
    player.onPositionChanged.listen((Duration d) {
      setState(() => currentPlayTime = d.inSeconds);
    });
  }

  @override
  void dispose() {
    controller.dispose();
    player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final double height = MediaQuery.sizeOf(context).height;
    return Scaffold(
      // backgroundColor: Colors.white,
      appBar: AppBar(title: Text(widget.place.name)),
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.all(8),
          child: Center(
            child: Column(
              children: [
                _PlaceImageView(imageUrls: widget.place.images, height: height),
                const SizedBox(height: 16),
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    "Thuyết minh (${widget.audioGuides.length})",
                    style: TextStyle(fontSize: 20),
                  ),
                ),
                const SizedBox(height: 4),
                Expanded(
                  child: ListView.separated(
                    shrinkWrap: true,
                    itemBuilder: (BuildContext context, int index) {
                      return AudioGuideCard(
                        audioGuide: widget.audioGuides[index],
                        onTap: (audioGuide) async {
                          setState(() {
                            currentPlayTime = 0;
                            currentAudioGuide = audioGuide;
                          });
                          await player.stop();
                          try {
                            final audioUrl = await Amplify.Storage.getUrl(
                              path: StoragePath.fromString(audioGuide.audioUrl),
                            ).result;
                            safePrint(audioUrl.url);
                            await player.play(
                              UrlSource(audioUrl.url.toString()),
                            );
                          } catch (ex) {
                            safePrint(ex);
                          }
                        },
                      );
                    },
                    separatorBuilder: (BuildContext context, int index) {
                      return SizedBox(height: 8);
                    },
                    itemCount: widget.audioGuides.length,
                  ),
                ),
                const SizedBox(height: 16),
                // _PlayerView(
                //   currentPlayTime: currentPlayTime,
                //   maxPlaytime: currentAudioGuide?.durationSeconds,
                //   isPlaying: player.state == PlayerState.playing,
                // ),
                // if (false)
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (currentAudioGuide != null) ...[
                      Align(
                        alignment: Alignment.center,
                        child: Text(currentAudioGuide!.title),
                      ),
                      SizedBox(height: 4),
                    ],
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4.0),
                      child: SliderTheme(
                        data: SliderTheme.of(context).copyWith(
                          thumbShape: RoundSliderThumbShape(
                            enabledThumbRadius: 6.0,
                          ),
                          overlayShape: RoundSliderOverlayShape(
                            overlayRadius: 12.0,
                          ),
                        ),
                        child: Slider(
                          value: currentAudioGuide == null
                              ? 0
                              : currentPlayTime.toDouble(),
                          max:
                              currentAudioGuide?.durationSeconds.toDouble() ??
                              0,
                          onChanged: (double value) {},
                        ),
                      ),
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Text(
                          durationSecondsToString(currentPlayTime),
                          style: TextStyle(fontSize: 12),
                        ),
                        if (currentAudioGuide != null)
                          Text(
                            durationSecondsToString(
                              currentAudioGuide!.durationSeconds,
                            ),
                            style: TextStyle(fontSize: 12),
                          ),
                        if (currentAudioGuide == null)
                          Text("--:--", style: TextStyle(fontSize: 12)),
                      ],
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        IconButton(
                          onPressed: () async {
                            if (currentAudioGuide == null) {
                              return;
                            }
                            await player.seek(
                              Duration(seconds: min(0, currentPlayTime - 10)),
                            );
                          },
                          icon: Icon(Icons.replay_10),
                        ),
                        if (player.state == PlayerState.playing)
                          IconButton(
                            onPressed: () async {
                              await player.pause();
                            },
                            icon: Icon(Icons.pause),
                          ),
                        if (player.state != PlayerState.playing)
                          IconButton(
                            onPressed: () async {
                              if (player.state == PlayerState.paused) {
                                await player.resume();
                              } else {
                                await player.seek(Duration(seconds: 0));
                                await player.resume();
                              }
                            },
                            icon: Icon(Icons.play_arrow),
                          ),
                        IconButton(
                          onPressed: () async {
                            if (currentAudioGuide == null) {
                              return;
                            }
                            await player.seek(
                              Duration(
                                seconds: min(
                                  currentAudioGuide!.durationSeconds,
                                  currentPlayTime + 10,
                                ),
                              ),
                            );
                          },
                          icon: Icon(Icons.forward_10),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _PlaceImageView extends StatefulWidget {
  final List<String> imageUrls;
  final double height;

  const _PlaceImageView({required this.imageUrls, required this.height});

  @override
  State<_PlaceImageView> createState() => _PlaceImageViewState();
}

class _PlaceImageViewState extends State<_PlaceImageView> {
  final CarouselController controller = CarouselController(initialItem: 1);

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: BoxConstraints(maxHeight: widget.height / 3),
      child: Column(
        children: [
          Align(
            alignment: Alignment.centerLeft,
            child: Text(
              "Hình ảnh (${widget.imageUrls.length})",
              style: TextStyle(fontSize: 20),
            ),
          ),
          const SizedBox(height: 4),
          Expanded(
            child: CarouselView.weighted(
              controller: controller,
              itemSnapping: true,
              flexWeights: const <int>[1, 8, 1],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadiusGeometry.circular(8),
              ),
              children: widget.imageUrls.map((String url) {
                return Image.network(url, fit: BoxFit.cover);
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}

class _PlayerView extends StatelessWidget {
  final String? title;
  final int currentPlayTime;
  final int? maxPlaytime;

  final Function? onReplay10Tap;
  final Function? onForward10Tap;
  final Function? onPlayPauseTap;
  final bool isPlaying;

  const _PlayerView({
    this.title = "",
    required this.currentPlayTime,
    this.maxPlaytime = 0,
    this.onReplay10Tap,
    this.onForward10Tap,
    this.onPlayPauseTap,
    required this.isPlaying,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Align(alignment: Alignment.center, child: Text(title ?? "")),
        SizedBox(height: 4),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4.0),
          child: SliderTheme(
            data: SliderTheme.of(context).copyWith(
              thumbShape: RoundSliderThumbShape(enabledThumbRadius: 6.0),
              overlayShape: RoundSliderOverlayShape(overlayRadius: 12.0),
            ),
            child: Slider(
              value: currentPlayTime.toDouble(),
              max: maxPlaytime?.toDouble() ?? 0,
              onChanged: (double value) {},
            ),
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Text(
              durationSecondsToString(currentPlayTime),
              style: TextStyle(fontSize: 12),
            ),
            Text(
              durationSecondsToString(maxPlaytime ?? 0),
              style: TextStyle(fontSize: 12),
            ),
          ],
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            IconButton(
              onPressed: () {
                onReplay10Tap?.call();
              },
              icon: Icon(Icons.replay_10),
            ),
            IconButton(
              onPressed: () {
                onPlayPauseTap?.call();
              },
              icon: Icon(isPlaying ? Icons.pause : Icons.play_arrow),
            ),
            IconButton(
              onPressed: () {
                onForward10Tap?.call();
              },
              icon: Icon(Icons.forward_10),
            ),
          ],
        ),
      ],
    );
  }
}
