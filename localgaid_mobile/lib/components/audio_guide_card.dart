import 'package:flutter/material.dart';
import 'package:localgaid_mobile/domain_models/audio_guide.dart';

class AudioGuideCard extends StatelessWidget {
  final AudioGuide audioGuide;
  final Function(AudioGuide)? onTap;

  const AudioGuideCard({super.key, required this.audioGuide, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        onTap?.call(audioGuide);
      },
      child: Container(
        height: 56,
        padding: EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(4),
        ),
        child: Row(
          children: [
            Icon(Icons.play_arrow),
            SizedBox(width: 8),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    audioGuide.title,
                    style: TextStyle(overflow: TextOverflow.ellipsis),
                  ),
                  Text(
                    audioGuide.duration,
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
